#-*- coding:utf-8 -*-
'''
doctest

  >>> print filter('adgwwWvaaW')
  wwWvW

  >>> start('wWWwwww')
  w

'''

__version__ = '0.0.0'
__author__ = 'shomah4a'


import sys
import os

try:

    from pypy.rlib.jit import JitDriver
    jitdriver = JitDriver(greens=['function', 'arg'],
                          reds=['env'])
except:

    class jitdriver:

        @staticmethod
        def jit_merge_point(**kw):
            pass



def is_n(st):

    def call(c):

        return c in st

    return call


is_w = is_n(u'wｗ')
is_W = is_n(u'WＷ')
is_v = is_n(u'vｖ')


def count_n(pred):

    def call(inp):

        count = 0
        n = len(inp)

        while 1:

            if count >= n:
                break

            if not pred(inp[count]):
                break

            count += 1

        return count, inp[count:]

    return call


count_w = count_n(is_w)
count_W = count_n(is_W)
count_v = count_n(is_v)



def filter(inp):

    ret = ''

    for i in inp:

        if is_w(i) or is_W(i) or is_v(i):
            ret += i

    return ret



class StackItem(object):

    def apply(self, obj):
        pass



class FunCall(object):
    u'''
    関数呼び出し
    '''

    def __init__(self, f, a):

        self.func = f
        self.arg = a


    def apply(self, env):

        function = env[-self.func]
        arg = env[-self.arg]

        jitdriver.jit_merge_point(env=env, function=function,
                                  arg=arg)


        ret = function.apply(arg)

        env.append(ret)


    def __repr__(self):

        return '<%s (%s, %s)>' % (FunCall.__name__, self.func, self.arg)



class Function(StackItem):
    u'''
    関数
    '''

    def __init__(self, count, calls, env):

        self.count = count
        self.env = env[:]
        self.calls = calls


    def apply(self, arg):

        if self.count != 1:
            return Function(self.count-1, self.calls, self.env+[arg])

        env = self.env[:]
        env.append(arg)

        for call in self.calls:
            call.apply(env)

        return env[-1]


    def __repr__(self):

        return '<%s (%s)%s>' % (Function.__name__, self.count, ([(x.func, x.arg) for x in self.calls]))



class Succ(StackItem):
    u'''
    加算
    '''

    def apply(self, arg):

        return Char((arg.value+1) & 255)




class Out(StackItem):
    u'''
    出力
    '''

    def apply(self, arg):

        os.write(1, chr(arg.value))

        return arg
    


class In(StackItem):
    u'''
    入力
    '''

    def apply(self, arg):

        v = os.read(0, 1)[0]

        if not v:
            return arg

        return Char(ord(v))



class Char(StackItem):

    def __init__(self, val):

        self.value = val
        

    def apply(self, arg):

        if self == arg:
            return Function(1, [FunCall(3, 2)], [Function(1, [], [])])

        return Function(1, [], [])



def parse_abs(inp, env):

    argc, left = count_w(inp)

    apps = []

    while left:

        if is_v(left[0]):
            left = left[1:]
            break

        app, left = parse_app(left, env)
        apps.append(app)

    return Function(argc, apps, env), left



def parse_app(inp, env):

    f, left = count_W(inp)

    a, left = count_w(left)

    return FunCall(f, a), left



def parse_prog(inp, env):

    f, left = parse_abs(inp, env)
    env.append(f)

    while left:
        n = left[0]
        
        if is_w(n):
            f, left = parse_abs(left, env)
            env.append(f)
        elif is_W(n):
            break


    while left:
        n = left[0]

        if is_W(n):
            app, left = parse_app(left, env)
            app.apply(env)
        else:
            break

    return env



def parse(inp):

    env = [In(),
           Char(ord('w')),
           Succ(),
           Out()]

    parse_prog(inp, env)

    return env


def run(env):

    try:
        f = env[-1]
        f.apply(f)
    except Exception, e:
        print e



def start(inp):

    run(parse(filter(inp)))
    print



def main(argv):

    if len(argv) < 1:
        print 'no input file'
        return 1

    f = argv[1]

    fp = os.open(f, os.O_RDONLY, 0777)

    buf = ""
    while True:
        d = os.read(fp, 4096)
        if len(d) == 0:
            break
        buf += d

    os.close(fp)

    start(buf)

    return 0


def target(*args):
    return main, None


def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()



if __name__ == '__main__':

    main(sys.argv)

    


