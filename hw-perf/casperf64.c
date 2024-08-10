#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    void* spam = malloc(8);  // 64bits

    for (int i = 0; i < 4294967295UL; i++) {
        __sync_bool_compare_and_swap_8(spam, 0, 0);
    }
    
    free(spam);

    return 0;
}
