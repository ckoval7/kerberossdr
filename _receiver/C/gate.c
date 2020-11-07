/* KerberosSDR Gate
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


//#define BUFFER_SIZE 1024 * 128 * 4//1024*256*4
#define CFN "_receiver/C/gate_control_fifo" // Name of the gate control fifo - Control FIFO name

//#define BUFFER_SIZE 256 * 1024 * 4

int BUFFER_SIZE = 0;

static sem_t trigger_sem;
static volatile int trigger=0, exit_flag=0;
pthread_t fifo_read_thread;   
void * fifo_read_tf(void* arg) 
{
/*          FIFO read thread function
 * 
 */
    fprintf(stderr,"FIFO read thread is running\n");    
    FILE * fd = fopen(CFN, "r"); // FIFO descriptor
    if(fd!=0)
        fprintf(stderr,"FIFO opened\n");
    else
        fprintf(stderr,"FIFO open error\n");
    uint8_t trigger_read;
    while(1){
        fread(&trigger_read, sizeof(trigger_read), 1, fd);
        if( (uint8_t) trigger_read == 1)
        {
            //fprintf(stderr,"Trigger received\n");
            trigger++;
            sem_wait(&trigger_sem);          
        }            
        else if( (uint8_t) trigger_read == 2)
        {
            fprintf(stderr,"[ EXIT ] FIFO read thread exiting \n");
            exit_flag = 1;
            break;
        }
    }
    fclose(fd);
    return NULL;
}


int main(int argc, char** argv)
{

    //static char buf[262144 * 4 * 30];
    //setvbuf(stdout, buf, _IOFBF, sizeof(buf));


    BUFFER_SIZE = atoi(argv[1]) * 1024 * 4;

    int read_size;
    uint8_t * buffer;    

    sem_init(&trigger_sem, 0, 0);  // Semaphore is unlocked    
    pthread_create(&fifo_read_thread, NULL, fifo_read_tf, NULL);
    
    // Allocate sample buffer
   // uint8_t buffer[BUFFER_SIZE];
    buffer= malloc(BUFFER_SIZE*sizeof(uint8_t));

    fprintf(stderr,"Start gate control\n");    
    while(1)
    {        
        if(feof(stdin))
            break;
        
        read_size = fread(buffer,sizeof(*buffer), BUFFER_SIZE, stdin);

        //read_size = read(STDIN_FILENO, buffer, BUFFER_SIZE);        
        if(read_size>0)
        {
            if(trigger == 1)
            {

                fwrite(buffer, sizeof(*buffer), read_size, stdout);
                fflush(stdout);
                trigger --;
                sem_post(&trigger_sem);
            }            
            else
            {
                //fprintf(stderr,"No trigger, dropping %d samples..\n", read_size);
            }
            
            if(exit_flag)
              break;  
            
        }
        
    }    
    pthread_join(fifo_read_thread, NULL);
    sem_destroy(&trigger_sem);
    fprintf(stderr,"[ EXIT ] Gate control exited\n");
    return 0;
    
}

