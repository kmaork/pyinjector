static void init(void) __attribute__((constructor));

static void init(void) {
    const char *s = "Hello, world!";
    write(1, s, strlen(s));
    close(1);
}