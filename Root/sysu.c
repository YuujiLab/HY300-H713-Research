#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    if (setgid(0) != 0 || setuid(0) != 0) {
        perror("setuid/setgid");
        return 1;
    }

    if (argc > 1) {
        execvp(argv[1], &argv[1]);
    } else {
        execl("/system/bin/sh", "sh", NULL);
    }

    perror("exec");
    return 1;
}
