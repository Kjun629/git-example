#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include<stdlib.h>
#include<time.h>
#include<sys/time.h>

#define NUMTHRDS 8
#define NUM 45000000

typedef struct
{
    int thread_id;
    int start;
    int end;
    double *cnt;
} Arg; // 傳入 thread 的參數型別

pthread_t callThd[NUMTHRDS]; // 宣告建立 pthread
pthread_mutex_t mutexsum;    // pthread 互斥鎖

// 每個 thread 要做的任務
void *count_pi(void *arg)
{

    Arg *data = (Arg *)arg;
    int thread_id = data->thread_id;
    int start = data->start;
    int end = data->end;
    double *cnt = data->cnt;

    // 將原本的 PI 算法切成好幾份
    double x, y, count=0;
    double n = NUM;
    for (int i = start; i < end; i++)
    {
        x = ((double)rand()/(double)RAND_MAX);
        y = ((double)rand()/(double)RAND_MAX);
        if((x*x+y*y)<1){
            count++;
        }
    }

    // **** 關鍵區域 ****
    // 一次只允許一個 thread 存取
    pthread_mutex_lock(&mutexsum);
    // 將部分的 PI 加進最後的 PI
    *cnt += count;
    pthread_mutex_unlock(&mutexsum);
    // *****************
    printf("Thread %d did %d to %d:  cnt=%lf\n", thread_id, start, end, *cnt);
    pthread_exit((void *)0);
}

int main(int argc, char *argv[])
{
    // 初始化互斥鎖
    pthread_mutex_init(&mutexsum, NULL);

    // 設定 pthread 性質是要能 join
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

    // 每個 thread 都可以存取的 PI
    // 因為不同 thread 都要能存取，故用指標
    double *cnt = malloc(sizeof(*cnt));
    double pi=0;
    *cnt = 0;

    int part = NUM / NUMTHRDS;

    Arg arg[NUMTHRDS]; // 每個 thread 傳入的參數
    //  計時
    clock_t start, end;
    start = clock();//
    for (int i = 0; i < NUMTHRDS; i++)
    {
        // 設定傳入參數
        arg[i].thread_id = i;
        arg[i].start = part * i;
        arg[i].end = part * (i + 1);
        arg[i].cnt = cnt;

        // 建立一個 thread，執行 count_pi 任務，傳入 arg[i] 指標參數
        pthread_create(&callThd[i], &attr, count_pi, (void *)&arg[i]);
    }

    // 回收性質設定
    pthread_attr_destroy(&attr);

    void *status;
    for (int i = 0; i < NUMTHRDS; i++)
    {
        // 等待每一個 thread 執行完畢
        pthread_join(callThd[i], &status);
    }
    pi = (double)(4*(double)*cnt/(double)NUM);
    end = clock();
    double diff = end - start; // ms
    // 所有 thread 執行完畢，印出 PI
    printf("Pi =  %f \n", pi);
    printf(" %f  sec\n", diff / CLOCKS_PER_SEC );
    // 回收互斥鎖
    pthread_mutex_destroy(&mutexsum);
    // 離開
    pthread_exit(NULL);
}
