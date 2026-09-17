package ru.railbrake.calculator.core

import java.io.File
import java.security.MessageDigest
import java.util.zip.GZIPInputStream
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class ErmakRelatedIndexTest {
    @Test fun preservesAllCanonicalLinks() {
        val root = JSONObject(GZIPInputStream(File("src/main/assets/technical/ermak_links.json.gz").inputStream()).bufferedReader().use { it.readText() })
        val ids = sortedSetOf<String>()
        fun visit(value: Any?) {
            when (value) {
                is JSONObject -> value.keys().forEach { key ->
                    if (key.startsWith("ER-") || key.startsWith("SYS-")) ids.add(key)
                    visit(value.opt(key))
                }
                is JSONArray -> for (i in 0 until value.length()) visit(value.opt(i))
                is String -> if (listOf("ER-EQ-", "ER-KB-", "ER-DIAG-", "ER-SCH-", "ER-VARIANT-", "SYS-").any(value::startsWith)) ids.add(value)
            }
        }
        visit(root.getJSONObject("indexes"))
        val index = ErmakRelatedIndex(root)
        val actual = ids.joinToString("") { id -> "$id\t${index.relatedTo(id).sorted().joinToString(",")}\n" }
        val digest = MessageDigest.getInstance("SHA-256").digest(actual.toByteArray()).joinToString("") { "%02x".format(it) }
        // Golden generated from Recovery8's original lookup for every canonical ID.
        assertEquals(421, ids.size)
        assertEquals("d507bdf496e442a3e5df1387b2686197fc06296218b7585b0744fd89c98437c2", digest)
        assertTrue(index.relatedTo("missing").isEmpty())
    }

    @Test fun includesReverseLinksAndDropsSelfAndDuplicateReferences() {
        val index = ErmakRelatedIndex(JSONObject("""{"indexes":{"byEquipment":{"ER-EQ-A":{"nested":["ER-EQ-A","ER-DIAG-B","ER-DIAG-B","metadata"]}}}}"""))
        assertEquals(listOf("ER-DIAG-B"), index.relatedTo("ER-EQ-A"))
        assertEquals(listOf("ER-EQ-A"), index.relatedTo("ER-DIAG-B"))
        assertTrue(index.relatedTo("metadata").isEmpty())
    }
}
