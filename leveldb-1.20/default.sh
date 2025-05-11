
export cores=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28)
export mutex_cores=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28)
export ncores=28
export root_dir=/home/haoling/TCLocks
export results_dir=${root_dir}/doc/results
export runtime=30
export kernel=`uname -r | sed 's/5.14.16-//'`

## For python-environment
export python_env_cores='[1,2,4,8,12,16,20,28,56,84,112,128,168,224]'
