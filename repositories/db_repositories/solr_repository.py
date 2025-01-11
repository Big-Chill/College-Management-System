import pysolr
from .base_repository import IDBRepository


class SolrRepository(IDBRepository):
    def __init__(self, solr_url: str):
        self.client = pysolr.Solr(solr_url, always_commit=True, timeout=10)

    def insert(self, table: str, data: dict):
        try:
            resp = self.client.add([data])
        except Exception as e:
            raise Exception(f"Error indexing data in Solr: {str(e)}")

    def select(self, table: str, conditions: str):
        try:
            # Modify the conditions for partial and fuzzy search automatically
            conditions = self.apply_partial_search(conditions)
            conditions = self.apply_fuzzy_search(conditions)
            conditions = self.apply_wildcard_search(conditions)

            # Execute the Solr search with the modified conditions
            search_obj = self.client.search(conditions)
            search_results = search_obj.docs

            # Flatten the fields for each result
            results = [self.flatten_fields(result) for result in search_results]

            # Return the processed results
            return results

        except Exception as e:
            raise Exception(f"Error querying Solr: {str(e)}")

    def flatten_fields(self, result):
        """
        Flatten any fields that are lists and ensure the result is in normal form.
        """
        flattened_result = {}
        for field, value in result.items():
            if isinstance(value, list):
                # If the value is a list, extract the first item if it's a single value field
                flattened_result[field] = value[0] if len(value) == 1 else value
            else:
                flattened_result[field] = value
        return flattened_result

    def apply_fuzzy_search(self, query: str, fuzziness: float = 0.8):
        """
        Apply fuzzy search to the query by appending a tilde (~) and fuzziness factor.
        """
        # Fuzzy search: add ~ to the query and apply fuzziness factor
        return f"{query}~{fuzziness}"

    def apply_partial_search(self, query: str):
        """
        Apply partial search by using wildcard at the end of the query.
        """
        # Partial search: append * to the query for prefix matching
        return f"{query}*"

    def apply_wildcard_search(self, query: str):
        """
        Apply wildcard search by ensuring * or ? is included.
        If no wildcard is present, append a * for suffix matching.
        """
        # Wildcard search: if query contains neither '*' nor '?', treat it as a suffix wildcard
        if '*' not in query and '?' not in query:
            return f"{query}*"
        return query

    def remove_all_data(self):
        try:
            self.client.delete(q='*:*')
        except Exception as e:
            raise Exception(f"Error clearing Solr data: {str(e)}")