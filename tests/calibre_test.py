import pytest

from calibre_rest.calibre import CalibreWrapper
from calibre_rest.errors import CalibreRuntimeError
from calibre_rest.models import Book

dud_wrapper = CalibreWrapper("foo", "bar")


def test_run_executable_err(calibre):
    cmd = "hello world"
    with pytest.raises(SystemExit, match="You must specify a command from"):
        calibre._run(cmd)


def test_run_success(calibre):
    cmd = f"{calibre.cdb} --version"
    out, err = calibre._run(cmd)

    assert "__main__" in out
    assert err == ""


@pytest.mark.parametrize(
    "keys, expected",
    (
        pytest.param(["id"], "--ascending --sort-by=id", id="ascending"),
        pytest.param(["-id"], "--sort-by=id", id="descending"),
        pytest.param(
            ["title", "authors", "uuid"],
            "--ascending --sort-by=title,authors,uuid",
            id="multiple",
        ),
        pytest.param(
            ["title", "authors", "-uuid"],
            "--sort-by=title,authors,uuid",
            id="multiple descending",
        ),
        pytest.param([], "--ascending", id="empty"),
        pytest.param(["not_exist"], "--ascending", id="invalid"),
        pytest.param(
            ["title", "not_exist"],
            "--ascending --sort-by=title",
            id="mixed invalid",
        ),
    ),
)
def test_handle_sort(keys, expected):
    cmd = ["calibredb", "list"]
    dud_wrapper._handle_sort(cmd, keys)
    assert cmd == ["calibredb","list"] + expected.split()


@pytest.mark.parametrize(
    "search, expected",
    (
        pytest.param(["title:foo"], ['--search', 'title:foo'], id="single"),
        pytest.param(
            ["title:foo", "id:5", "series:bar"],
            ['--search', "title:foo id:5 series:bar"],
            id="multiple",
        ),
        pytest.param(["title:^f*"], ['--search', "title:^f*"], id="regex"),
        pytest.param([], [], id="empty"),
    ),
)
def test_handle_search(search, expected):
    cmd = ["calibredb", "list"]
    dud_wrapper._handle_search(cmd, search)
    assert cmd == ["calibredb", "list"] + expected


@pytest.mark.parametrize(
    "book, expected",
    (
        (
            Book(title="foobar", series_index=4.5),
            ["calibredb", "add", "--series-index", 4.5, "--title", "foobar"],
        ),
        (
            Book(identifiers={"isbn": "abcd", "asin": 1234}),
            ["calibredb", "add", "--identifier", "isbn:abcd", "--identifier", "asin:1234"],
        ),
    ),
    ids=["simple", "identifiers"],
)
def test_handle_add_flags_simple(book, expected):
    cmd = ["calibredb", "add"]
    dud_wrapper._handle_add_flags(cmd, book)

    assert cmd == expected


def test_handle_add_flags_list():
    cmd = ["calibredb", "add"]
    book = Book(tags=["foo", "bar", "example"])
    dud_wrapper._handle_add_flags(cmd, book)
    expected = "calibredb add --tags foo,bar,example".split()

    assert cmd == expected


def test_handle_add_flags_list_with_spaces():
    cmd = ["calibredb", "add"]
    book = Book(
        authors=["John Doe", " Ben Adams"],
        languages=["english ", " french"],
        tags=["foo", "bar", " two words "],
    )
    dud_wrapper._handle_add_flags(cmd, book)
    expected = ["calibredb", "add", "--authors", 'John Doe & Ben Adams', "--languages", "english,french", "--tags", 'foo,bar,two words']

    assert cmd == expected


@pytest.mark.parametrize(
    "book, expected",
    (
        (Book(title="foobar", id=1234), "calibredb add --title foobar".split()),
        (Book(pubdate="1234", size=1234), "calibredb add".split()),
    ),
    ids=["valid and invalid", "all invalid"],
)
def test_handle_add_flags_invalid(book, expected):
    cmd = ["calibredb", "add"]
    dud_wrapper._handle_add_flags(cmd, book)

    assert cmd == expected


@pytest.mark.parametrize(
    "book, expected",
    (
        (Book(title="foobar"), "calibredb set_metadata 1 --field title:foobar"),
        (Book(series_index=4.0), "calibredb set_metadata 1 --field series_index:4.0"),
    ),
)
def test_handle_update_flags(book, expected):
    cmd = "calibredb set_metadata 1".split()
    dud_wrapper._handle_update_flags(cmd, book)
    assert cmd == expected.split()


def test_handle_update_flags_list():
    cmd = "calibredb set_metadata 1".split()
    book = Book(tags=["foo", "bar"])

    dud_wrapper._handle_update_flags(cmd, book)
    expected = "calibredb set_metadata 1 --field tags:foo,bar".split()

    assert cmd == expected


def test_handle_update_flags_list_with_spaces():
    cmd = "calibredb set_metadata 1".split()
    book = Book(tags=["foo", "bar", " two words"])

    dud_wrapper._handle_update_flags(cmd, book)
    expected = ["calibredb", "set_metadata", "1", "--field", "tags:foo,bar,two words"]

    assert cmd == expected


def test_handle_update_flags_authors():
    cmd = "calibredb set_metadata 1".split()
    book = Book(authors=["John Doe", " Ben Adams"])

    dud_wrapper._handle_update_flags(cmd, book)
    expected = ["calibredb", "set_metadata", "1", "--field", "authors:John Doe & Ben Adams"]

    assert cmd == expected


def test_handle_update_flags_identifiers():
    cmd = "calibredb set_metadata 1".split()
    book = Book(identifiers={"isbn": 1234, "asin": "abcd"})

    dud_wrapper._handle_update_flags(cmd, book)
    expected = "calibredb set_metadata 1 --field identifiers:isbn:1234,asin:abcd".split()

    assert cmd == expected


@pytest.mark.parametrize(
    "book, expected",
    (
        (
            Book(title="foobar", uuid="abcd1234"),
            "calibredb set_metadata 1 --field title:foobar",
        ),
        (Book(uuid="1234", cover="test"), "calibredb set_metadata 1"),
    ),
)
def test_handle_update_flags_invalid(book, expected):
    cmd = "calibredb set_metadata 1".split()
    dud_wrapper._handle_update_flags(cmd, book)
    assert cmd == expected.split()
