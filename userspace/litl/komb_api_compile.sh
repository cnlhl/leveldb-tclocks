# 编译 .c 文件为 .o 文件
gcc -g -O0 -fPIC -c src/komb_api.c src/komb.c src/utils.c -I./include -DFCT_LINK_SUFFIX=KOMB -DWAITING_SPIN_THEN_PARK -DCOND_VAR=1

# 链接为共享库
sudo gcc -shared -o /usr/local/lib/libkomb_api.so komb_api.o komb.o utils.o

# 注册共享库（可选但推荐）
sudo ldconfig

# 编译示例程序，链接共享库
gcc -g -O0 examples/komb_example.c -o komb_example -I./include -L/usr/local/lib -lkomb_api -lpthread

gcc -g -O0 examples/lock_benchmark.c -o lock_benchmark -I./include -L/usr/local/lib -lkomb_api -lpthread

gcc -g -O0 examples/rate_profiler.c -o rate_profiler -I./include -L/usr/local/lib -lkomb_api -lpthread