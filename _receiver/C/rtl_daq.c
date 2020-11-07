/* KerberosSDR Python GUI
 *
 * Copyright (C) 2018-2019  Carl Laufer, Tamás Peto
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *
 *
 * Project : KerberosSDR
 * Object  : Coherent multichannel receiver for the RTL chipset based software defined radios
 * Date    : 2018 09 10 - 2019 02 07
 * State   : Production
 * Version : 0.1
 * Author  : Tamás Peto
 * Modifcations : Carl Laufer
 *
 *
 *
 */
/* Compile like this:
gcc -std=c99 rtl_rec.h rtl_daq.c -lpthread -lrtlsdr -o rtl_daq
*/

#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <unistd.h>
#include <assert.h>

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <time.h>
#include <stdbool.h>

#include "rtl-sdr.h"
// TODO: Remove unnecessary includes
#include "rtl_rec.h"

#define NUM_CH 4  // Number of receiver channels
#define NUM_BUFF 1 // Number of buffers
//#define BUFF_LEN (16*16384) //(16 * 16384)
#define SAMPLE_RATE 2000000
#define CENTER_FREQ 107200000
#define GAIN 5

#define CFN "_receiver/C/rec_control_fifo" /* Receiver control FIFO name */
#define NOTUSED(V) ((void) V)
#define ASYNC_BUF_NUMBER     12

#define DEFAULT_RATE         2000000
#define DEFAULT_FREQ         107200000

int BUFF_LEN = 0;

struct rtl_rec_struct* rtl_receivers;
pthread_mutex_t buff_ind_mutex;
pthread_mutex_t fifo_mutex;
pthread_cond_t buff_ind_cond;
pthread_t fifo_read_thread;

int reconfig_trigger=0, exit_flag=0;
int noise_source_state = 0;
int last_noise_source_state = 0;

unsigned int read_buff_ind = 0;

bool writeOrder[4];

unsigned int writeCount = 0;


void * fifo_read_tf(void* arg)
{
    /*          FIFO read thread function
    *
    */

    uint8_t signal;
    int gain_read = GAIN;
    int gain_read_2 = GAIN;
    int gain_read_3 = GAIN;
    int gain_read_4 = GAIN;

    int gain_read_array[4];

    uint32_t center_freq_read = CENTER_FREQ, sample_rate_read = SAMPLE_RATE;
    FILE * fd = fopen(CFN, "r"); // FIFO descriptor    
    (void)arg;     
    
    fprintf(stderr,"FIFO read thread is running\n");    
    if(fd!=0)
        fprintf(stderr,"FIFO opened\n");
    else
        fprintf(stderr,"FIFO open error\n");
    while(!exit_flag){
        fread(&signal, sizeof(signal), 1, fd);
        //pthread_mutex_lock(&buff_ind_mutex);    
    


        if( (uint8_t) signal == 2)
        {            
            //fprintf(stderr,"Signal2: FIFO read thread exiting \n");
            exit_flag = 1;           
        }
        else
        {            
            reconfig_trigger=1;
        }


        if( (char) signal == 'r')
        {
            //fprintf(stderr,"Signal 'r': Reconfiguring tuner \n");
            fread(&center_freq_read, sizeof(uint32_t), 1, fd);
            fread(&sample_rate_read, sizeof(uint32_t), 1, fd);
            fread(&gain_read, sizeof(int), 1, fd);

            fread(&gain_read_2, sizeof(int), 1, fd);
            fread(&gain_read_3, sizeof(int), 1, fd);
            fread(&gain_read_4, sizeof(int), 1, fd);

            gain_read_array[0] = gain_read;
            gain_read_array[1] = gain_read_2;
            gain_read_array[2] = gain_read_3;
            gain_read_array[3] = gain_read_4;
            
            //fprintf(stderr,"[ INFO ] Center freq: %u MHz\n", ((unsigned int) center_freq_read/1000000));
            //fprintf(stderr,"[ INFO ] Sample rate: %u MSps\n", ((unsigned int) sample_rate_read/1000000));
            //fprintf(stderr,"[ INFO ] Gain: %d dB\n",(gain_read/10));
            
            for(int i=0; i<NUM_CH; i++)
            {              
              rtl_receivers[i].gain = gain_read_array[i];
              rtl_receivers[i].center_freq = center_freq_read;
              rtl_receivers[i].sample_rate = sample_rate_read;
            }            

            for(int i=0; i<NUM_CH; i++)
            {                
                if(rtlsdr_cancel_async(rtl_receivers[i].dev) != 0)
                {
                    fprintf(stderr, "[ ERROR ]  Async read stop failed: %s\n", strerror(errno));                
                }
                //fprintf(stderr, "[ INFO ] Async read stopped at device:%d\n",i);
            }



        }
	else if ( (char) signal == 'n')
        {
            //fprintf(stderr,"Signal 'n': Turn on noise source \n");            
            noise_source_state = 1;
	    reconfig_trigger = 0;

            rtlsdr_set_gpio(rtl_receivers[0].dev, 1, 0);

        }
        else if ( (char) signal == 'f')
        {
            //fprintf(stderr,"Signal 'f': Turn off noise source \n");            
            noise_source_state = 0;
            reconfig_trigger = 0;
            rtlsdr_set_gpio(rtl_receivers[0].dev, 0, 0);

        }
  
        //pthread_cond_signal(&buff_ind_cond);
        //pthread_mutex_unlock(&buff_ind_mutex);
    }
    fclose(fd);
    return NULL;
}


void rtlsdrCallback(unsigned char *buf, uint32_t len, void *ctx)
{
        //pthread_mutex_lock(&buff_ind_mutex);

        struct rtl_rec_struct *rtl_rec = (struct rtl_rec_struct *) ctx;// Set the receiver's structure

        /*if (len != BUFF_LEN)
        {
            fprintf(stderr, "[ DEBUG ] Len greather than BUFF_LEN\n");
            len = BUFF_LEN;   
        }*/
    
        writeOrder[rtl_rec->dev_ind] = true;
    	memcpy(rtl_rec->buffer, buf, len);
        //fprintf(stderr, "Read_buff_ind:%d, rtl_recbuff_ind:%d\n",rtl_rec->buff_ind, rtl_rec->buff_ind);
        if(writeOrder[0] && writeOrder[1] && writeOrder[2] && writeOrder[3])
        {
           pthread_cond_signal(&buff_ind_cond);
        }
        //pthread_mutex_unlock(&buff_ind_mutex);
}



void *read_thread_entry(void *arg)
{

    //fprintf(stderr, "[ DEBUG ] Pointer value %p\n", arg);
    struct rtl_rec_struct *rtl_rec = (struct rtl_rec_struct *) arg;// Set the thread's own receiver structure   
    //fprintf(stderr, "[ INFO ] Initializing RTL-SDR device, index:%d\n", rtl_rec->dev_ind);   
   
    rtlsdr_dev_t *dev = NULL;
   
    dev = rtl_rec->dev;

    if (rtlsdr_set_dithering(dev, 0) !=0) // Only in keenerd's driver
    {
        fprintf(stderr, "[ ERROR ] Failed to disable dithering: %s\n", strerror(errno));
    }
    if (rtlsdr_set_tuner_gain_mode(dev, 1) !=0)
    {
        fprintf(stderr, "[ ERROR ] Failed to disbale AGC: %s\n", strerror(errno));
    }
    if (rtlsdr_reset_buffer(dev) !=0)
    {
        fprintf(stderr, "[ ERROR ] Failed to reset receiver buffer: %s\n", strerror(errno));
    }
    
    while(!exit_flag)
    {
   
        //CHECK1(rtlsdr_set_testmode(dev, 1)); // Set this to enable test mode
        if (rtlsdr_set_center_freq(dev, rtl_rec->center_freq) !=0)
        {
            fprintf(stderr, "[ ERROR ] Failed to set center frequency: %s\n", strerror(errno));
        }

        if (rtlsdr_set_tuner_gain(dev, rtl_rec->gain) !=0)
        {
            fprintf(stderr, "[ ERROR ] Failed to set gain value: %s\n", strerror(errno));
        }   
        if (rtlsdr_set_sample_rate(dev, rtl_rec->sample_rate) !=0)
        {
            fprintf(stderr, "[ ERROR ] Failed to set sample rate: %s\n", strerror(errno));
        }
        //fprintf(stderr, "[ DONE ] Device is initialized %d\n", rtl_rec->dev_ind);
        rtlsdr_read_async(dev, rtlsdrCallback, rtl_rec, ASYNC_BUF_NUMBER, BUFF_LEN);       
    
    }
    
    
    fprintf(stderr, "[ INFO ] Device:%d handler thread exited\n", rtl_rec->dev_ind);

return NULL;
}

int main( int argc, char** argv )
{
    //static char buf[262144 * 4 * 30];

    //setvbuf(stdout, NULL, _IOFBF, 0);
    fprintf(stderr, "[ INFO ] Starting multichannel coherent RTL-SDR receiver\n");


    writeOrder[0] = false;
    writeOrder[1] = false;
    writeOrder[2] = false;
    writeOrder[3] = false;


    BUFF_LEN = (atoi(argv[1])/16) * 16384;

    // Allocation
    rtl_receivers = malloc(sizeof(struct rtl_rec_struct)*NUM_CH);
    for(int i=0; i<NUM_CH; i++)
    {
        struct rtl_rec_struct *rtl_rec = &rtl_receivers[i];        
        memset(rtl_rec, 0, sizeof(struct rtl_rec_struct));
        rtl_rec->dev_ind = i;        
    }
   
    // Initialization
    for(int i=0; i<NUM_CH; i++)
    {
        struct rtl_rec_struct *rtl_rec = &rtl_receivers[i];
        rtl_rec->buff_ind=0;        
        rtl_rec->gain = GAIN;
        rtl_rec->center_freq = CENTER_FREQ;
        rtl_rec->sample_rate = SAMPLE_RATE;
        rtl_rec->buffer = malloc(NUM_BUFF * BUFF_LEN * sizeof(uint8_t));
	//rtlsdr_set_gpio(rtl_rec->dev, 0, 0);
      
        if(! rtl_rec->buffer)
        {
            fprintf(stderr, "[ ERROR ] Data buffer allocation failed. Exiting..\n");   
            exit(1);
        }
           
    }
    pthread_mutex_init(&buff_ind_mutex, NULL);
    pthread_cond_init(&buff_ind_cond, NULL); 

    // we're going to test the "data_ready, exit_flag and reconfig_trigger" so we need the mutex for safety
    pthread_mutex_lock(&buff_ind_mutex);

   
    for(int i=0; i<NUM_CH; i++)
    {
    	struct rtl_rec_struct *rtl_rec = &rtl_receivers[i];// Set the thread's own receiver structure      
    	rtlsdr_dev_t *dev = NULL;
   
    	if (rtlsdr_open(&dev, rtl_rec->dev_ind) !=0)
    	{
       		//fprintf(stderr, "[ ERROR ] Failed to open RTL-SDR device: %s\n", strerror(errno));
    	}
    	rtl_rec->dev = dev;
    }

/*
    for(int i=0; i<NUM_CH; i++)
    {
    	struct rtl_rec_struct *rtl_rec = &rtl_receivers[i];// Set the thread's own receiver structure      
   
    	if (rtlsdr_init(rtl_rec->dev) !=0)
    	{
       		//fprintf(stderr, "[ ERROR ] Failed to open RTL-SDR device: %s\n", strerror(errno));
    	}
    }
*/

    int rc;
    pthread_attr_t attr;
    struct sched_param param;
    rc = pthread_attr_init (&attr);
    rc = pthread_attr_getschedparam(&attr, &param);
    //rc = pthread_attr_setschedpolicy(&attr, SCHED_RR);

    
    // Spawn reader threads
    for(int i=0; i<NUM_CH; i++)
    {       
        //(param.sched_priority)++;
        rc = pthread_attr_setschedparam(&attr, &param);
        pthread_create(&rtl_receivers[i].async_read_thread, &attr, read_thread_entry, &rtl_receivers[i]);           
    }

    // Spawn control thread
    pthread_create(&fifo_read_thread, NULL, fifo_read_tf, NULL);
   
     
  //unsigned long long read_buff_ind = 0;
  int data_ready = 1;
  struct rtl_rec_struct *rtl_rec;
  
  

  while( !exit_flag )
  {  
     
      /* block this thread until another thread signals cond. While
      blocked, the mutex is released, then re-aquired before this
      thread is woken up and the call returns. */
      pthread_cond_wait( &buff_ind_cond, &buff_ind_mutex);

      //data_ready = 0;
      // Do we have new data ready for the processing?

      //if(writeOrder[0] && writeOrder[1] && writeOrder[2] && writeOrder[3])
      //{
          //fprintf(stderr, "[ INFO ] Writing data to stdout, buff ind:%lld \n",read_buff_ind);

          /*if (last_noise_source_state != noise_source_state)
          {
              rtl_rec = &rtl_receivers[0];
              if (noise_source_state == 1)
                  rtlsdr_set_gpio(rtl_rec->dev, 1, 0);
	      else if (noise_source_state == 0)
	          rtlsdr_set_gpio(rtl_rec->dev, 0, 0);
          }

          last_noise_source_state = noise_source_state;*/
          //Adding a delay seems to help stop problems with the sync being lost
          //usleep(1000000);

          for(int i=0; i < NUM_CH; i++)
          {
              writeOrder[i] = false;

              rtl_rec = &rtl_receivers[i];
              fwrite(rtl_rec->buffer, BUFF_LEN, 1, stdout);
              fflush(stdout);
          }
          /*writeOrder[0] = false;
          writeOrder[1] = false;
          writeOrder[2] = false;
          writeOrder[3] = false;*/
          //fflush(stdout);

          /* We need to reconfigure the tuner, so the async read must be stopped*/
          /*if(reconfig_trigger==1)
          {
            reconfig_trigger=0;
          }*/

      //}
     
     
     
     /* Waiting for new data or reconfiguration command*/
     
   }
 
  fprintf(stderr, "[ INFO ] Exiting\n");  
  for(int i=0; i<NUM_CH; i++)
  {     
    struct rtl_rec_struct *rtl_rec = &rtl_receivers[i];
    if(rtlsdr_cancel_async(rtl_rec->dev) != 0)
    {
        fprintf(stderr, "[ ERROR ]  Async read stop failed: %s\n", strerror(errno));
        exit(1);
    }
    fprintf(stderr, "[ INFO ] Async read stopped at device:%d\n",i);        
    pthread_join(rtl_rec->async_read_thread, NULL);
    free(rtl_rec->buffer);
    
    /* This is does not work currently, TODO: Close the devices properly
    if(rtlsdr_close(rtl_rec->dev) != 0)
    {
        fprintf(stderr, "[ ERROR ]  Device close failed: %s\n", strerror(errno));
        exit(1);
    }
    fprintf(stderr, "[ INFO ] Device closed with id:%d\n",i);
    */
  }
  pthread_mutex_unlock(&buff_ind_mutex);
  pthread_join(fifo_read_thread, NULL);
  fprintf(stderr, "[ INFO ] All the resources are free now\n");
  //TODO: Free up buffers and join pthreads
  return 0;
}

