#include <stdlib.h>
#include <string.h>
#include <unistd.h>

const char *message = "Injected!\n";

__attribute__((constructor))
static void init()
{
    write(1, message, strlen(message));
    exit(0);
}
