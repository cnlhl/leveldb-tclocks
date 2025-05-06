# 编译 .c 文件为 .o 文件
gcc -g -O0 -fPIC -c src/komb_api.c src/kombmtx.c src/utils.c -I./include -DFCT_LINK_SUFFIX=KOMBMTX -DWAITING_SPIN_THEN_PARK

# 链接为共享库
sudo gcc -shared -o /usr/local/lib/libkomb_api.so komb_api.o kombmtx.o utils.o

# 注册共享库（可选但推荐）
sudo ldconfig

# 编译示例程序，链接共享库
gcc -g -O0 examples/komb_example.c -o komb_example -I./include -L/usr/local/lib -lkomb_api -lpthread
