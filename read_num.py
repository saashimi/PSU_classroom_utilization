def read_num():
    try:
        value = int(input("Type in a number. > ")
    except NameError:
        value = int(input("Invalid Input. > "))
    return value

def printOutput(lst):
    print(len(lst))
    print(lst)
    print(sum(lst)


def main():
    lst1 = []
    value = read_num()
    while value != 0:
        lst1 += [value]
        value = read_num()
    printOutput(lst1)  

##   

main()
