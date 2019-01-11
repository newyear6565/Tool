#from multiprocessing import Pool
import threading

def func(indx):
    time.sleep(3)
    filename = "tmp_file_" + str(indx) + ".txt"
    fp = open(filename, "w")
    fp.write("I'm done!")
    fp.close()

def call_back(indx):
    print("%d is done!"%indx)


def driver():

    for i in range(0, 3):
        print("Now is starting thread: %d"%i)
        result = pool.apply_async(func, [i], call_back)

if __name__ == '__main__':
    driver()
