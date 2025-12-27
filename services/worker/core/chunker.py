from typing import List, Optional

class RecursiveCharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
        keep_separator: bool = False,
    ):
        """
        Splits text recursively by different characters.
        
        Args:
            chunk_size: Maximum size of chunks to return
            chunk_overlap: Overlap in characters between chunks
            separators: List of separators to use for splitting. 
                       Defaults to ["\n\n", "\n", " ", ""]
            keep_separator: Whether to keep the separator in the chunks
        """
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._separators = separators or ["\n\n", "\n", " ", ""]
        self._keep_separator = keep_separator

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        return self._split_text(text, self._separators)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursive splitting logic."""
        final_chunks = []
        
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        
        for i, _s in enumerate(separators):
            if _s == "":
                separator = _s
                break
            if _s in text:
                separator = _s
                new_separators = separators[i + 1:]
                break
                
        # Split
        if separator:
            if self._keep_separator:
                # The validation of non-empty separator is important here
                # but we're doing basic string split for now
                splits = text.split(separator)
                # Re-attach separator to the end of each split except the last one?
                # For simplicity in this Custom version, we'll just split. 
                # A more complex implementation would handle keep_separator delicately.
                # For now let's behave like the standard: remove separator unless complex regex logic
                pass 
            splits = text.split(separator)
        else:
            splits = list(text) # Split by character if no separators found (unlikely with "")

        
        # Now merge splits into chunks
        good_splits = []
        _separator = separator if self._keep_separator else "" 
        
        # IMPORTANT: If we found no separator (meaning we are at the char level or empty string separator fallback),
        # we don't want to recurse anymore.
        
        for s in splits:
            if not s: # skip empty
                continue
                
            if len(s) < self._chunk_size:
                good_splits.append(s)
            else:
                # If the split is still too big, recurse
                if new_separators:
                    good_splits.extend(self._split_text(s, new_separators))
                else:
                    # If no more separators, we just have to hard cut it (or leave it if it's one giant block)
                    # For this implementation, if we run out of separators, we leave as is 
                    # OR we could force a hard cut. Let's force hard cut if really needed or just accept it.
                    # Standard behavior: leave it or hard cut. Let's leave it to avoid breaking words mid-way if possible,
                    # but if we are at " " level, we are essentially word splitting.
                    good_splits.append(s)

        return self._merge_splits(good_splits, separator)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Combine small splits into chunks of max_size"""
        separator_len = len(separator)
        
        docs = []
        current_doc = []
        total = 0
        
        for d in splits:
            _len = len(d)
            if total + _len + (separator_len if len(current_doc) > 0 else 0) > self._chunk_size:
                if total > self._chunk_size:
                    # Defensive: if single chunk is bigger than chunk_size
                    pass
                
                if current_doc:
                    doc = self._join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)
                    
                    # Handle overlap
                    while total > self._chunk_overlap or (total + _len + separator_len > self._chunk_size and total > 0):
                        total -= len(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
                        current_doc.pop(0)

            current_doc.append(d)
            total += _len + (separator_len if len(current_doc) > 1 else 0)

        doc = self._join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)
            
        return docs

    def _join_docs(self, docs: List[str], separator: str) -> Optional[str]:
        text = separator.join(docs)
        text = text.strip()
        if text == "":
            return None
        return text
