#include <stdlib.h>
#include <pthread.h>


void *thread_routine(void *spam) {
    for (int i = 0; i < 4294967295UL; i++) {
        __sync_bool_compare_and_swap_1(spam, 0, 0);
    }

    return spam;
}

int main(void) {
    pthread_t thread1, thread2;
    void* spam = malloc(1);  // 8bits

    int t1 = pthread_create(&thread1, NULL, thread_routine, (void*) spam);
    int t2 = pthread_create(&thread2, NULL, thread_routine, (void*) spam);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    return t1 + t2;
}
