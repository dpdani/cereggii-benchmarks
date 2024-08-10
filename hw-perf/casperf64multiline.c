#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    void* spam = aligned_alloc(64, 64 + 64);  // 2 lines

    for (int i = 0; i < 1048576UL; i++) {  // that's ~MAX_UNSIGNED_LONG/4096
        __sync_bool_compare_and_swap_8(spam + 60, 0, 0); // over 2 lines
        // last 4 bytes of the first line + first 4 bytes of the second line
    }

    free(spam);

    return 0;
}
