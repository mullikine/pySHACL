# -*- coding: utf-8 -*-
from collections import defaultdict

from pyshacl.consts import RDF_type, SH_TripleRule, SH_SPARQLRule, SH_SPARQLFunction, SH_rule, SH_condition
from pyshacl.errors import RuleLoadError
from pyshacl.shapes_graph import ShapesGraph
from pyshacl.rules.shacl_rule import SHACLRule
from pyshacl.rules.triple import TripleRule
from pyshacl.rules.sparql import SPARQLRule

ALL_SPARQL_RULES = [
    TripleRule,
    SPARQLRule
]


def gather_functions(shacl_graph):
    """

    :param shacl_graph:
    :type shacl_graph: ShapesGraph
    :return:
    :rtype: [SHACLRule]
    """
    fn_nodes = set(shacl_graph.subjects(RDF_type, SH_SPARQLFunction))
    if len(fn_nodes):
        raise NotImplementedError("SHACL Advanced Feature SPARQLFunction is not yet supported.")


def gather_rules(shacl_graph):
    """

    :param shacl_graph:
    :type shacl_graph: ShapesGraph
    :return:
    :rtype: [SHACLRule]
    """
    triple_rule_nodes = set(shacl_graph.subjects(RDF_type, SH_TripleRule))
    sparql_rule_nodes = set(shacl_graph.subjects(RDF_type, SH_SPARQLRule))
    overlaps = triple_rule_nodes.intersection(sparql_rule_nodes)
    if len(overlaps) > 0:
        raise RuleLoadError(
            "A SHACL Rule cannot be both a TripleRule and a SPARQLRule.",
            "https://www.w3.org/TR/shacl-af/#rules-syntax")
    used_rules = shacl_graph.subject_objects(SH_rule)
    ret_rules = defaultdict(list)
    for sub, obj in used_rules:
        try:
            shape = shacl_graph.lookup_shape_from_node(sub)
        except (AttributeError, KeyError):
            raise RuleLoadError(
                "The shape that rule is attached to is not a valid SHACL Shape.",
                "https://www.w3.org/TR/shacl-af/#rules-syntax")
        if obj in triple_rule_nodes:
            rule = TripleRule(shape, obj)
        elif obj in sparql_rule_nodes:
            rule = SPARQLRule(shape, obj)
        else:
            raise RuleLoadError(
                "when using sh:rule, the Rule must be defined as either a TripleRule or SPARQLRule.",
                "https://www.w3.org/TR/shacl-af/#rules-syntax")
        ret_rules[shape].append(rule)
    return ret_rules


def apply_rules(shapes_rules, data_graph):
    # short the shapes dict by shapes sh:order before execution
    shapes_rules = sorted(shapes_rules.items(), key=lambda x: x[0].order)
    for shape, rules in shapes_rules:
        # sort the rules by the sh:order before execution
        rules = sorted(rules, key=lambda x: x.order)
        for r in rules:
            if r.deactivated:
                continue
            r.apply(data_graph)

