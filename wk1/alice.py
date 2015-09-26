

def open_file():
    filename = input("Input filename. > ")
    open_text = open(filename, 'r')
    print("Opened " + filename)
    return open_text 

def parse_file(blarg):
    word_dct = {}
    for line in blarg:
        raw_output = line.split() # these are all strings
        for str_ in raw_output:
            word_dct[str_] = 0
    return word_dct

def search_dict(dct):
    """input: a dictionary with keys and 0 values.
       output: a dictionary with keys and counted value
    """
    for word in dct:
        if word in dct:
            dct[word] += 1
        else:
            dct[word] + 1 
    return dct    


def main():
    foo = open_file()
    bar = parse_file(foo)
    foo1 = search_dict(bar)
    #for counts in foo1.values():
    #    counts.sort(reverse = True)
    print(foo1)
    
"""Unit Tests"""

def unit_tests():
    file = open('test.txt', 'r') # loads separate test file
    assert parse_file(file) == {'string' : 0}
    assert search_dict({'string' : 0,}) == {'string' : 1}
    file.close()
print("Passed all tests.")

#def search_dict_test():
      
main()    
unit_tests()

