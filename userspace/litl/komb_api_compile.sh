# 编译 .c 文件为 .o 文件 (加入 -g)
gcc -g -O0 -fPIC -c src/komb_api.c src/kombmtx.c src/utils.c -I./include -DFCT_LINK_SUFFIX=KOMBMTX -DWAITING_SPIN_THEN_PARK

# 链接 .o 文件为 .so 共享库 (这条通常不需要加 -g，调试信息来自 .o 文件)
sudo gcc -shared -o /usr/local/lib/libkomb_api.so komb_api.o kombmtx.o utils.o

gcc -g -O0 examples/komb_example.c -o komb_example -I./include -L. -lkomb_api -lpthread