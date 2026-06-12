import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.embedder import Embedder
from backend.app.services.llm import LocalLLM
from backend.app.services.parser import DocumentParser


class TestTextilBotRAG(unittest.TestCase):
    def test_chunking(self):
        text = "Cette reglementation definit les exigences d'etiquetage pour les vetements composes a 100% de coton."
        chunks = DocumentParser.chunk_text(text, chunk_size=20, overlap=5)
        self.assertTrue(len(chunks) > 0)
        self.assertIn("coton", chunks[-1])

    def test_out_of_scope_detection(self):
        self.assertTrue(LocalLLM.check_out_of_scope("Quelle est la recette d'une pizza margherita ?"))
        self.assertFalse(LocalLLM.check_out_of_scope("Quelle est la regle pour etiqueter le coton ?"))

    def test_embedder_dimension(self):
        self.assertEqual(Embedder.get_dimension(), 384)

    def test_response_generation_with_no_contexts_uses_textile_fallback(self):
        resp, ctx = LocalLLM.generate_response("Quel est l'etiquetage du coton ?", [])
        self.assertIn("Coton", resp)
        self.assertEqual(len(ctx), 0)

    def test_compliance_status_is_deterministic(self):
        analysis, status, confidence, references = LocalLLM.generate_compliance_analysis(
            product_name="T-shirt",
            fiber_composition="80% coton, 10% polyester",
            intended_market="Union Europeenne",
            label_text="80% coton, 10% polyester",
            contexts=[],
        )
        self.assertEqual(status, "non_compliant")
        self.assertGreater(confidence, 0.9)
        self.assertTrue(references)
        self.assertIn("90", analysis)


if __name__ == "__main__":
    unittest.main()
