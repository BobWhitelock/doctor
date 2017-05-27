
def available_aliases(doc_sets, aliases_map):
    """Gives map from available names to doc set they resolves as.

    All doc sets in `doc_sets` will be included mapped to themselves, along
    with any additional mappings to these doc sets from the `aliases_map`.
    """
    available = {doc: doc for doc in doc_sets}
    available.update({
        alias: doc for alias, doc in aliases_map.items()
        if doc in doc_sets
    })
    return available
