def generate_5k():
    return 'a'*10000

def generate_10k():
    return 'a'*10000

def generate_20k():
    return 'a'*20000

def generate_50k():
    return 'a'*50000

def generate_100k():
    return 'a'*100000

def generate_500k():
    return 'a'*500000

def generate_1000k():
    return 'a'*1000000

def generate_5000k():
    return 'a'*5000000

def generate_10000k():
    return 'a'*10000000

def no_op(arg):
    return arg

def no_op_list(*args):
    return args

if __name__ == '__main__':
    import cloudpickle
    cloudpickle.dump(generate_5k, open('generate_5k.pickle', 'wb'))
    cloudpickle.dump(generate_10k, open('generate_10k.pickle', 'wb'))
    cloudpickle.dump(generate_20k, open('generate_20k.pickle', 'wb'))
    cloudpickle.dump(generate_50k, open('generate_50k.pickle', 'wb'))
    cloudpickle.dump(generate_100k, open('generate_100k.pickle', 'wb'))
    cloudpickle.dump(generate_500k, open('generate_500k.pickle', 'wb'))
    cloudpickle.dump(generate_1000k, open('generate_1000k.pickle', 'wb'))
    cloudpickle.dump(generate_5000k, open('generate_5000k.pickle', 'wb'))
    cloudpickle.dump(generate_10000k, open('generate_50000k.pickle', 'wb'))
    cloudpickle.dump(no_op, open('no_op.pickle', 'wb'))
    cloudpickle.dump(no_op_list, open('no_op_list.pickle', 'wb'))