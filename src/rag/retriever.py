import glob
import os
import re
from typing import Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RUNBOOKS_DIR = os.path.join(os.path.dirname(__file__), "runbooks")

class RunbookChunk:
    def __init__(self, runbook_name: str, title: str, section: str, content: str):
        self.runbook_name = runbook_name
        self.title = title
        self.section = section
        self.content = content

    def to_dict(self, score: float = 0.0) -> Dict:
        return {
            "runbook": self.runbook_name,
            "title": self.title,
            "section": self.section,
            "content": self.content,
            "relevance_score": round(float(score), 4),
        }

class RunbookRetriever:
    """
    RAG semantic search retriever that chunks SRE runbooks
    and retrieves top matching troubleshooting guidelines for active incidents.
    """

    def __init__(self, runbooks_dir: Optional[str] = None):
        self.runbooks_dir = runbooks_dir or RUNBOOKS_DIR
        self.chunks: List[RunbookChunk] = []
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        """Parse all markdown runbooks and build chunk indices."""
        md_files = glob.glob(os.path.join(self.runbooks_dir, "*.md"))
        chunks = []

        for fpath in md_files:
            fname = os.path.basename(fpath)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract top title
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            main_title = title_match.group(1).strip() if title_match else fname

            # Split by markdown H2 headings
            sections = re.split(r"\n##\s+", content)
            for idx, sec in enumerate(sections):
                if not sec.strip():
                    continue
                lines = sec.strip().split("\n", 1)
                sec_heading = lines[0].strip()
                sec_body = lines[1].strip() if len(lines) > 1 else lines[0].strip()

                chunk = RunbookChunk(
                    runbook_name=fname,
                    title=main_title,
                    section=sec_heading,
                    content=sec_body,
                )
                chunks.append(chunk)

        self.chunks = chunks
        if self.chunks:
            corpus = [f"{c.title} {c.section} {c.content}" for c in self.chunks]
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Query index and return top-k most relevant runbook sections."""
        if not self.chunks or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.05:  # Relevance threshold
                results.append(self.chunks[idx].to_dict(score))

        return results
