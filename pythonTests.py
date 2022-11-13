test = 0


def fun_test():
    global test
    test = test + 1


def fun_test_2():
    global test
    test = test + 1
    print(test)


if __name__ == '__main__':
    fun_test()
    fun_test_2()
    test = test + 1
    fun_test_2()