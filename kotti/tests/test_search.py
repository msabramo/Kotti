from kotti.testing import DummyRequest


def create_contents(root=None):
    from kotti.resources import get_root
    from kotti.resources import Content, File
    if root is None:
        root = get_root()
    doc1 = root['doc1'] = Content(title=u'First Document')
    doc11 = root['doc1']['doc11'] = Content(title=u'Second Document')
    doc12 = root['doc1']['doc12'] = Content(title=u'Third Document')
    file1 = root['doc1']['file1'] = File(title=u'First File',
                                         description=u'this is a file')
    return doc1, doc11, doc12, file1


class TestSearch:

    def test_search_empty_content(self, db_session):
        from kotti.views.util import search_content
        request = DummyRequest()
        results = search_content(u'teststring', request)
        assert results == []

    def test_search_content(self, db_session):
        from kotti.views.util import search_content
        request = DummyRequest()
        doc1, doc11, doc12, file1 = create_contents()
        results = search_content(u'First Document', request)
        assert len(results) == 1
        assert results[0]['name'] == u'doc1'
        assert results[0]['title'] == u'First Document'
        results = search_content(u'Document', request)
        # The frontpage contains 'Documentation' in its body!
        assert len(results) == 4
        assert results[1]['name'] == u'doc11'
        assert results[1]['title'] == u'Second Document'
        assert results[1]['path'] == '/doc1/doc11/'
        assert results[-1]['path'] == '/'

        # Tag searching first splits the search term on blanks, then uses
        # kotti.views.util.content_with_tags(tags) to find content tagged by
        # the single word terms resulting from the split. Tags with blanks in
        # them are not identified in the simple default treatment, so here we
        # use single-word tags in the same way that the default Search works.
        doc1.tags = [u'animal', u'cat']
        doc11.tags = [u'animal', u'dog']
        doc12.tags = [u'animal', u'monkey', u'health']
        file1.tags = [u'animal', u'monkey', u'health']
        results = search_content(u'animal', request)
        assert len(results) == 4
        results = search_content(u'dog', request)
        assert len(results) == 1
        results = search_content(u'dog monkey health', request)
        assert len(results) == 3
        results = search_content(u'health', request)
        assert len(results) == 2

    def test_search_file_description(self, db_session):
        from kotti.views.util import search_content
        request = DummyRequest()
        doc1, doc11, doc12, file1 = create_contents()
        results = search_content(u'this is a file', request)
        assert len(results) == 1
        assert results[0]['name'] == 'file1'
        assert results[0]['title'] == 'First File'
        assert results[0]['path'] == '/doc1/file1/'

    def test_search_content_without_permission(self, config, db_session):
        from kotti.views.util import search_content
        request = DummyRequest()
        create_contents()
        config.testing_securitypolicy(permissive=False)
        results = search_content(u'Document', request)
        assert len(results) == 0
