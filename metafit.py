import random
import math
import copy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sympy import *

class Object:
    pass

class Expression:
    CST="cst"
    VAR="var"
    ADD="+"
    SUB="-"
    MUL="*"
    DIV="/"
    POW="^"
    EXP="exp"
    LOG="log"
    SIN="sin"
    COS="cos"
    NOP="_"

    DUAL_OPS=[ADD,SUB,MUL,DIV,POW,NOP]
    SINGLE_OPS=[EXP,LOG,SIN,COS]

    def __init__(self):
        self.expr=[(Expression.CST,0)]
        self.max_len = 50

    def str(self):
        return str(self.expr)

    def evaluate(self,variables):
        stack=[]
        for op, value in self.expr:
            if op==Expression.CST:
                stack.append(value)
            elif op==Expression.VAR:
                stack.append(variables[value%len(variables)])
            elif op==Expression.ADD:
                b=stack.pop()
                a=stack.pop()
                stack.append(a+b)
            elif op==Expression.SUB:
                b=stack.pop()
                a=stack.pop()
                stack.append(a-b)
            elif op==Expression.MUL:
                b=stack.pop()
                a=stack.pop()
                stack.append(a*b)
            elif op==Expression.DIV:
                b=stack.pop()
                a=stack.pop()
                stack.append(a/b)
            elif op==Expression.POW:
                b=stack.pop()
                a=stack.pop()
                stack.append(a**b)
            elif op==Expression.NOP:
                stack.pop()

        if len(stack) != 1:
            raise

        return stack[0]

    def addRandomValue(self):
        if random.randrange(1,3) == 2:
            self.expr.append((Expression.VAR,random.randrange(0,100000)))
        else:
            self.expr.append((Expression.CST,random.uniform(-2,2)))

    def addOp(self):
        op = random.choice(self.DUAL_OPS)
        self.expr.append((op,None))

    def mutateGrow(self):
        for i in range(random.randrange(1,3)):
            self.addRandomValue()

        self.addOp()

    def mutatePointHard(self):
        i=random.randrange(0,len(self.expr))
        v=random.randrange(1,4)
        if v == 1:
            self.expr[i]=(Expression.VAR,random.randrange(0,100000))
        elif v == 2:
            self.expr[i]=(Expression.CST,random.uniform(-2,2))
        elif v == 3:
            op = random.choice(self.DUAL_OPS)
            self.expr[i]=(op,None)

    def mutatePointSoft(self):
        i=random.randrange(0,len(self.expr))

        op, val = self.expr[i]
        if op==Expression.VAR:
            self.expr[i]=(Expression.VAR,random.randrange(0,100000))
        elif op==Expression.CST:
            if random.randrange(1,3) == 1:
               self.expr[i]=(Expression.CST,val+random.uniform(-val - random.uniform(1,10),val + random.uniform(1,10)))
            else:
               self.expr[i]=(Expression.CST,val*random.uniform(-1,1))

    def show(self,varcount):
        str=""
        for op,val in self.expr:
            if op == Expression.VAR:
                str+=("%s "% ( chr(ord("a")+(val%varcount)) ) )
            elif op == Expression.CST:
                str+="%.3f "%val
            else:
                str+=op+" "
        return str.strip()

    def show_infix(self,varcount):
        variables=[Symbol(chr(ord("a")+(i))) for i in range(varcount)]
        expr=self.evaluate(variables)
        return str(simplify(expr))

class Solution:
    def __init__(self,expr,dist):
        self.expr=expr
        self.dist=dist

class Approximator:
    def __init__(self):
        self.data=[]
        self.solution=None

        self.params = Object()
        self.params.varcount = None #Automatically set by addDataPoint
        self.params.distancemetric = lambda data, fit: abs(data-fit)
        self.params.annealiters = 100000
        self.params.annealsched = lambda k, maxk: (1.0 - k/maxk)
        self.params.annealacceptp = lambda T, old, new: math.exp(-((new - old)/old)/T)
        self.params.annealrelbest = True #Rate new solutions relative to best solution (otherwise: relative to current solution)
        self.params.hardp = 0.5 #Probability for hard mutations that can change operators (other mutations are soft, i.e. simple value change)
        self.params.extenditers = 10000 #Number of random extensions of which the best is chosen
        self.params.extendgrace = 10 #Number of extensions without improvement of the best solution, after which fitting will be concluded

        self.params.output_progress = True #Output after every step (instead of just at end)
        self.params.output_console = True
        self.params.output_console_debug = False
        self.params.output_solution_file = False #.txt
        self.params.output_plot_file = False #.png

        self.stats = Object()
        self.stats.iters = 0
        self.stats.grace = 0
        self.stats.evals = 0
        self.stats.failed_evals = 0
        self.stats.accepted = 0
        self.stats.improved = 0

    def init(self):
        self.solution = Solution(Expression(),self.rate(Expression()))

    def extend(self):
        if self.params.output_console_debug:
            print("Extend...")
        best_new=None
        for i in range(self.params.extenditers):
            new_solution=copy.deepcopy(self.solution)
            new_solution.dist=None
            while new_solution.dist == None:
                new_solution=copy.deepcopy(self.solution)
                new_solution.expr.mutateGrow()
                new_solution.dist=self.rate(new_solution.expr)
            if best_new == None or new_solution.dist < best_new.dist:
                best_new=copy.deepcopy(new_solution)
        self.solution.expr=best_new.expr
        self.solution.dist=best_new.dist

    def optimize(self):
        old_distance=self.solution.dist
        new=self.anneal(self.solution)
        self.solution=new

        if self.params.output_console_debug:
            print("\tdist: before: %.3f, after opt: %.3f; fit: %s"%(old_distance,new.dist,new.expr.show_infix(self.params.varcount)))

    def anneal(self,solution):
        if self.params.output_console_debug:
            print("Optimize (SA)...")
        best=copy.deepcopy(solution)
        for k in range(self.params.annealiters):
            T=self.params.annealsched(float(k),float(self.params.annealiters))
            new=copy.deepcopy(solution)

            if random.uniform(0,1) < self.params.hardp:
                new.expr.mutatePointHard()
            else:
                new.expr.mutatePointSoft()

            new.dist=self.rate(new.expr)

            if new.dist == None:
                continue

            if new.dist < best.dist:
                P=1
            else:
                if self.params.annealrelbest:
                    P=self.params.annealacceptp(T,best.dist,new.dist)
                else:
                    P=self.params.annealacceptp(T,solution.dist,new.dist)

            if P > random.uniform(0,1):
                self.stats.accepted+=1
                solution=new
                if solution.dist < best.dist:
                    if self.params.output_console_debug:
                        print(T,best.dist,new.dist,new.expr.show_infix(self.params.varcount))
                    best=copy.deepcopy(solution)
                    self.stats.improved+=1

        return best

    def addDataPoint(self,vars,value):
        self.data.append((vars,value))

        if self.params.varcount == None:
            self.params.varcount=len(vars)

    def rate(self,expr):
        self.stats.evals += 1
        dist=0
        for vars, val in self.data:
            try:
                dist+=self.params.distancemetric(val,expr.evaluate(vars))
            except:
                self.stats.failed_evals += 1
                return None

        return dist

    def plot(self,filename,title):
        plt.clf()
        if self.params.varcount!=1:
            raise

        xd=[]
        yd=[]
        for vars, value in self.data:
            xd.append(vars[0])
            yd.append(value)

        plt.ylim(min(yd),max(yd))

        plt.title(title)
        plt.plot(xd,yd,label="Data",color="r",lw=3,ls="--")

        yf=[]
        for _x in xd:
            yf.append(float(self.solution.expr.evaluate([_x])))
        plt.plot(xd,yf,ls="--",color="b",label="Fit")

        #plt.plot(xd,ys,label="Avg Fit",color="g",lw=3,ls="--")
        plt.legend()
        plt.savefig(filename)

    def write(self):
        if self.params.output_plot_file != False:
            if self.params.varcount == 1:
                self.plot(self.params.output_plot_file,"Best Distance %.3f"%(self.solution.dist))
            else:
                print("Plot output only supported for 1D problems")

        if self.params.output_solution_file != False:
            outh=open(self.params.output_solution_file,"w")
            outh.write("%.3f: %s\n"%(self.solution.dist,self.solution.expr.show_infix(self.params.varcount)))
            outh.close()

        if self.params.output_console:
            print("")
            print("fit:")
            print("")
            print("\tf(...) = %s"%self.solution.expr.show_infix(self.params.varcount))
            print("\terror: %.3f"%self.solution.dist)
            print("")
            print("stats:")
            print("")
            print("\titers: %d, grace: %d/%d"%(self.stats.iters,self.stats.grace,self.params.extendgrace) )
            print("\tSA accepted: %d (%d improved)"%(self.stats.accepted,self.stats.improved))
            print("\tfunc evals: %d (%d fail)"%(self.stats.evals,self.stats.failed_evals))
            print("")
            print("==============================================")


    def step(self):
        self.optimize()
        self.extend()
        self.stats.iters+=1

    def fit(self):
        grace = self.params.extendgrace
        self.stats.grace = grace
        dist = self.solution.dist
        while grace > 0:
            if self.params.output_progress:
                self.write()
            self.step()
            if self.solution.dist < dist:
                grace = self.params.extendgrace
                dist = self.solution.dist
            else:
                grace -= 1
            self.stats.grace = grace

        self.write()
        return self.solution
