from ocdsmerge.rules import get_merge_rules
from tests import schema_url, tags


def test_get_merge_rules_1_1():
    assert get_merge_rules(schema_url.format(tags['1.1'])) == {
        ('awards', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('contracts', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('contracts', 'relatedProcesses', 'relationship'): {'wholeListMerge'},
        ('date',): {'omitWhenMerged'},
        ('id',): {'omitWhenMerged'},
        ('parties', 'additionalIdentifiers'): {'wholeListMerge'},
        ('parties', 'roles'): {'wholeListMerge'},
        ('relatedProcesses', 'relationship'): {'wholeListMerge'},
        ('tag',): {'omitWhenMerged'},
        ('tender', 'additionalProcurementCategories'): {'wholeListMerge'},
        ('tender', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('tender', 'submissionMethod'): {'wholeListMerge'},

        # Deprecated
        ('awards', 'amendment', 'changes'): {'wholeListMerge'},
        ('awards', 'amendments', 'changes'): {'wholeListMerge'},
        ('awards', 'suppliers', 'additionalIdentifiers'): {'wholeListMerge'},
        ('buyer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'amendment', 'changes'): {'wholeListMerge'},
        ('contracts', 'amendments', 'changes'): {'wholeListMerge'},
        ('contracts', 'implementation', 'transactions', 'payee', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'implementation', 'transactions', 'payer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'amendment', 'changes'): {'wholeListMerge'},
        ('tender', 'amendments', 'changes'): {'wholeListMerge'},
        ('tender', 'procuringEntity', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'tenderers', 'additionalIdentifiers'): {'wholeListMerge'},
    }


def test_get_merge_rules_1_0():
    assert get_merge_rules(schema_url.format(tags['1.0'])) == {
        ('awards', 'amendment', 'changes'): {'wholeListMerge'},
        ('awards', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('awards', 'suppliers'): {'wholeListMerge'},
        ('buyer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'amendment', 'changes'): {'wholeListMerge'},
        ('contracts', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('date',): {'omitWhenMerged'},
        ('id',): {'omitWhenMerged'},
        ('ocid',): {'omitWhenMerged'},
        ('tag',): {'omitWhenMerged'},
        ('tender', 'amendment', 'changes'): {'wholeListMerge'},
        ('tender', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('tender', 'procuringEntity', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'submissionMethod'): {'wholeListMerge'},
        ('tender', 'tenderers'): {'wholeListMerge'},
    }
