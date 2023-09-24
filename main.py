# pylint : disable = all
from core.problem import Problem, judgement
from core.run import CPP


pro = Problem("example")
print(judgement(pro, """#include <bits/stdc++.h>
using namespace std;
signed main(){int x;cin>>x;cout<<x;return 0;}""", CPP))
