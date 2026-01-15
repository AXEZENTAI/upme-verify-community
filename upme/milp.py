from dataclasses import dataclass
from typing import Dict, List, Literal, Any, Optional, Tuple

Sense = Literal["<=", ">=", "=="]
VarType = Literal["BINARY", "INTEGER"]

@dataclass(frozen=True)
class MILPVar:
    name: str
    vtype: VarType
    lo: int = 0
    hi: int = 1

@dataclass(frozen=True)
class MILPConstraint:
    name: str
    coeff: Dict[str, int]
    sense: Sense
    rhs: int

@dataclass(frozen=True)
class MILPObjective:
    direction: Literal["min","max"]
    coeff: Dict[str, int]
    constant: int = 0

@dataclass
class MILPProblem:
    name: str
    variables: List[MILPVar]
    constraints: List[MILPConstraint]
    objective: MILPObjective
    metadata: Dict[str, Any]

def eval_linear(coeff: Dict[str,int], x: Dict[str,int]) -> int:
    return int(sum(int(c)*int(x.get(k,0)) for k,c in coeff.items()))

def check_constraint(con: MILPConstraint, x: Dict[str,int]) -> bool:
    lhs = eval_linear(con.coeff, x)
    if con.sense == "<=": return lhs <= con.rhs
    if con.sense == ">=": return lhs >= con.rhs
    if con.sense == "==": return lhs == con.rhs
    raise ValueError("Unknown sense")

def objective_value(obj: MILPObjective, x: Dict[str,int]) -> int:
    return eval_linear(obj.coeff, x) + int(obj.constant)

def solve_milp_exact(problem: MILPProblem, node_limit: int = 50000) -> dict:
    vars_order = [v.name for v in problem.variables]
    domains = {}
    for v in problem.variables:
        if v.vtype == "BINARY":
            domains[v.name] = (0,1)
        else:
            domains[v.name] = (int(v.lo), int(v.hi))

    maximizing = (problem.objective.direction == "max")
    best_x: Optional[Dict[str,int]] = None
    best_obj: Optional[int] = None
    nodes = 0

    def better(val: int, cur: Optional[int]) -> bool:
        if cur is None: return True
        return val > cur if maximizing else val < cur

    def dfs(i: int, a: Dict[str,int]):
        nonlocal nodes, best_x, best_obj
        if nodes >= node_limit: return
        nodes += 1
        if i == len(vars_order):
            # check all constraints
            for con in problem.constraints:
                if not check_constraint(con, a):
                    return
            val = objective_value(problem.objective, a)
            if better(val, best_obj):
                best_obj = val
                best_x = dict(a)
            return
        var = vars_order[i]
        lo, hi = domains[var]
        for v in range(lo, hi+1):
            a[var] = v
            dfs(i+1, a)
            a.pop(var, None)
            if nodes >= node_limit: break

    dfs(0, {})
    status = "OPTIMAL" if (nodes < node_limit and best_x is not None) else ("BEST_FOUND_WITHIN_NODE_LIMIT" if best_x is not None else "INFEASIBLE_OR_UNPROVEN")
    return {
        "certifier":"milp_exact_demo_enumeration",
        "status": status,
        "provable_optimality": (status == "OPTIMAL"),
        "best_x": best_x,
        "best_objective": best_obj,
        "nodes_visited": nodes,
        "node_limit": node_limit,
        "scope_note":"Community Edition demo certifier (finite enumeration). Enterprise adds stronger pruning and formats."
    }

def milp_from_json(spec: dict) -> MILPProblem:
    vars_ = [MILPVar(name=v["name"], vtype=v["type"], lo=int(v.get("lo",0)), hi=int(v.get("hi",1))) for v in spec["variables"]]
    cons_ = [MILPConstraint(name=c.get("name","c"), coeff={k:int(val) for k,val in c["coeff"].items()}, sense=c["sense"], rhs=int(c["rhs"])) for c in spec.get("constraints",[])]
    obj = spec["objective"]
    objective = MILPObjective(direction=obj.get("direction","max"), coeff={k:int(val) for k,val in obj["coeff"].items()}, constant=int(obj.get("constant",0)))
    return MILPProblem(name=spec.get("name","milp_problem"), variables=vars_, constraints=cons_, objective=objective, metadata=spec.get("metadata",{}))
