#include <unistd.h>
#include <stdio.h>

int main() {
    setresgid(1000,1000,1000);
    setresuid(1000,1000,1000);

    printf("uid=%d euid=%d\n", getuid(), geteuid());

    execl("/system/bin/sh","sh",NULL);
}
