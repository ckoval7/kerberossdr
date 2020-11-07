/* KerberosSDR Sync
 *
 * Copyright (C) 2018-2019  Carl Laufer, Tamás Pető
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
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include "sync.h"

//2097152 - Buff size for real work
//#define BUFFER_SIZE 128 * 1024 //128*1024 // Sample 
#define BUFFER_NO 2  // Buffer number
#define CHANNEL_NO 4 // Channel number
#define CFN "_receiver/C/sync_control_fifo" // Name of the gate control fifo - Control FIFO name

int BUFFER_SIZE = 0;

/*
 *  Signal definitions: 
 * 
 * 
 *      
 * 
 */

static sem_t trigger_sem;
static int trigger;
static int exit_flag = 0;
static int delays[CHANNEL_NO]; 
pthread_t fifo_read_thread;    
void * fifo_read_tf(void* arg) 
{
/*          FIFO read thread function
 * 
 */    
    fprintf(stderr,"FIFO read thread is running\n");    
    (void)arg; 
    FILE * fd = fopen(CFN, "r"); // FIFO descriptor    
    if(fd!=0)
        fprintf(stderr,"FIFO opened\n");
    else
        fprintf(stderr,"FIFO open error\n");
    uint8_t signal;
    while(1){
        fread(&signal, sizeof(signal), 1, fd);
        if( (uint8_t) signal == 1)
        {
            fprintf(stderr,"Signal1: trigger\n");
            trigger++;
            sem_wait(&trigger_sem);          
        }            
        else if( (uint8_t) signal == 2)
        {            
            fprintf(stderr,"Signal2: FIFO read thread exiting \n");
            exit_flag = 1;
            break;
        }
        else if( (char) signal == 'd')
        {
            //fprintf(stderr,"Signal 'd': Updating delay values \n");
            fread(delays, sizeof(*delays), 4, fd);
            for(int m=0; m < CHANNEL_NO; m++)     
                if(abs(delays[m]) < BUFFER_SIZE)
                {
                    //fprintf(stderr,"[ INFO ] Channel %d, delay value %d\n",m,delays[m]);
                    delays[m] *=2; // I and Q !
                }
                else
                {
                    //fprintf(stderr,"[ ERROR ] Delay value over buffer size: %d, Setting to zero\n",delays[m]);
                    delays[m] = 0;
                    //fprintf(stderr,"[ WARNING ]Channel %d, delay value %d\n",m,delays[m]);
                }
            trigger++; // Set trigger for updating delay values
            sem_wait(&trigger_sem);          

        }
    }
    fclose(fd);
    return NULL;
}


int main(int argc, char** argv)
{    

    //static char buf[262144 * 4 * 30];
    //setvbuf(stdout, buf, _IOFBF, sizeof(buf));

    BUFFER_SIZE = (atoi(argv[1])/2) * 1024;

    int read_size; // Stores the read bytes from stdin
    int first_read = 0;
    int write_index = BUFFER_NO-1; // Buffer index 0..BUFFER_NO-1
    uint8_t *read_pointer;
    
    /* Initializing signal thread */ 
    sem_init(&trigger_sem, 0, 0);  // Semaphore is unlocked
    trigger = 0;
   
    
    pthread_create(&fifo_read_thread, NULL, fifo_read_tf, NULL);

   
    // Initializing delay buffers
    struct sync_buffer_struct* sync_buffers;    
    sync_buffers = malloc(CHANNEL_NO*sizeof(*sync_buffers));
    for(int m=0;m<CHANNEL_NO;m++)
    {
        (sync_buffers + m * sizeof(*sync_buffers))->circ_buffer = malloc(BUFFER_NO*BUFFER_SIZE*2*sizeof(uint8_t)); // *2-> I and Q    
        (sync_buffers + m * sizeof(*sync_buffers))->delay = BUFFER_SIZE;//BUFFER_SIZE/2;  
        //fprintf(stderr,"ch: %d, Buff pointer: %p\n",m,(sync_buffers + m * sizeof(*sync_buffers))->circ_buffer);
    }
    
    fprintf(stderr,"Start delay sync test\n");
    while(!exit_flag)
    {      
        
        if(feof(stdin))
            break;    
        
        write_index = (write_index+1)% BUFFER_NO;            
        for(int m=0; m<CHANNEL_NO; m++)
        {
           
            /* Read into buffer*/
            read_size = fread((sync_buffers + m * sizeof(*sync_buffers))->circ_buffer +(BUFFER_SIZE*2*write_index)*sizeof(uint8_t), sizeof(uint8_t), (BUFFER_SIZE*2), stdin);                
            if(read_size == 0)
            {
                //fprintf(stderr,"Read error at channel: %d, wr_index: %d\n",m, write_index);
                exit_flag = 1;
                break;
            }
                
            /* Write from delay pointer*/ 
            int delay = (sync_buffers + m * sizeof(*sync_buffers))->delay;                   
            if(first_read == CHANNEL_NO)
            {
                if(write_index == 1)
                {
                    read_pointer = (sync_buffers + m * sizeof(*sync_buffers))->circ_buffer + sizeof(uint8_t) * delay;
                    fwrite(read_pointer , sizeof(uint8_t), BUFFER_SIZE*2, stdout);
                    fflush(stdout);
                }
                else // Write index must be 0
                {
                    // Write first chunk
                    read_pointer = (sync_buffers + m * sizeof(*sync_buffers))->circ_buffer + sizeof(uint8_t) * (delay+BUFFER_SIZE*2);
                    fwrite(read_pointer , sizeof(uint8_t), (BUFFER_SIZE*2-delay), stdout);                        
                 
                    //Write second chunk
                    read_pointer = (sync_buffers + m * sizeof(*sync_buffers))->circ_buffer;
                    fwrite(read_pointer , sizeof(uint8_t), delay, stdout);
                    fflush(stdout);
                }                   
            }
            else
                first_read ++; 
                
            /* Log */                
            //fprintf(stderr,"Channel: %d, wr_index: %d\n",m,write_index);
            //fprintf(stderr,"Delay %d\n", delay);
                

        }

        /* Trigger receiver, updating delay values*/
        if(trigger == 1)
        {              
            for(int k=0; k<CHANNEL_NO; k++)
            {
                (sync_buffers + k * sizeof(*sync_buffers))->delay += delays[k];
                delays[k] = 0;
            }
            trigger --;
            sem_post(&trigger_sem);
        }


        if(exit_flag)
            break;    
        
    }     
    
    /* Free up buffers */ 
    for(int m=0;m<CHANNEL_NO;m++)
    {
        free((sync_buffers + m * sizeof(*sync_buffers))->circ_buffer);       
    }
   
    fprintf(stderr,"[ EXIT ] Sync block exited\n");
    return 0;
    
}


