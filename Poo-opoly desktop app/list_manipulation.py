def alphabetise_list(input, is_sorted):
    if not is_sorted:
        output = sorted(input, key=lambda x: x[0])
    else:
        output = sorted(input, key=lambda x: x[0], reverse=True)
    return output    

def search_list(input_list, search_term): #really short 'return [item for item in input_list if search_term in item[0]]'
    search_term_list = search_term.split()
    output=[]
    for item in input_list:
        for word in search_term_list:
            if item[0].find(word) == -1: #will return -1 if word isn't found. item[0] is product name
                break
        else:                    #in python else can be used with for loop
            output.append(item)
    return output

def remove_duplicates(input_list):
    unique_list = []
    for item in input_list:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list

def price_rank_list(input_list, is_sorted):
    if not is_sorted:
        output = sorted(input_list, key=lambda x: float(x[1].replace("$", "")))
    else:
        output = sorted(input_list, key=lambda x: float(x[1].replace("$", "")), reverse=True)
    return output  

def remove_supermarket(input_list, supermarket_name):
    output_list = []
    for item in input_list:
        if item[4] != supermarket_name:
            output_list.append(item)
    return output_list

def discount_rank_list(input_list, is_sorted):
    if not is_sorted:
        output = sorted(input_list, key=lambda x: x[3])
    else:
        output = sorted(input_list, key=lambda x: x[3], reverse=True)
    return output 

def sort_by_supermarket(input_list, is_sorted):
    if not is_sorted:
        output = sorted(input_list, key=lambda x: x[4])
    else:
        output = sorted(input_list, key=lambda x: x[4], reverse=True)
    return output 
