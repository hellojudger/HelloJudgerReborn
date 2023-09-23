# pylint : disable = all
from core.problem import Problem, judgement
from core.run import CPP_14


pro = Problem("example")
print(judgement(pro, """#include <iostream>
signed main(){
    int x;std::cin>>x;
    if(x==1) x=2;
    std::cout<<x;
    return 0;
}""", CPP_14))
