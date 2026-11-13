# Reproducer: `dependable_element` docs are unavoidably `testonly`

Communication publishes verification reports for its dependable elements
(`mw_com`, `message_passing`) on its own GitHub Pages site. We would like to
mount those pages into the reference integration documentation instead of only
linking them. This branch shows why that currently does not work.

**Nothing here is meant to be merged.** The change deliberately breaks `//:docs`.

## The change

One line in the root [`BUILD`](../../BUILD):

```python
docs(
    bundles = DOCS_BUNDLES,
    data = ["@score_communication//score/mw/com/dependability:mw_com_rst"],
    known_good = "known_good.json",
    source_dir = "docs",
)
```

`<name>_rst` is the `sphinx_docs_library` that `dependable_element` generates in
"Step 4" *precisely so that an external Sphinx build can include the element's
pages*. `docs(data = ...)` is the documented way to add files to this project's
root bundle, so this is the natural attempt.

## Result

```bash
bazel build --nobuild \
  --extra_toolchains=//bazel/toolchains:score_ref_int_libclang_toolchain \
  //:docs
```

```
ERROR: BUILD:35:5: in _docs_bundle rule //:docs_bundle: non-test target
'//:docs_bundle' depends on testonly target
'@@score_communication+//score/mw/com/dependability:mw_com_rst'
and doesn't have testonly attribute set
ERROR: Analysis of target '//:docs' failed; build aborted: Analysis failed
```

Communication is pinned at `313f1178` per `known_good.json`. The
`--extra_toolchains` flag is unrelated to the problem; without it analysis stops
earlier on a missing `libclang` toolchain for `score_tooling`. CI hits the same
error through `//:docs_shim`.

`@score_communication//score/message_passing/dependability:dependable_element_message_passing_rst`
behaves identically.

## Why `testonly = False` is not the answer

`dependable_element` has a `testonly` parameter that only *defaults* to `True`,
so the obvious idea is to flip it. That does not help: the target graph
underneath `<name>_rst` is built out of Bazel **test rules**, and test rules are
unconditionally `testonly` — no attribute can turn that off.

`<name>_rst` has `srcs = [":<name>_index"]`, and `<name>_index` reaches test
rules through *three* independent attributes:

```
$ bazel query 'somepath(@score_communication//score/mw/com/dependability:mw_com_rst,
                        @score_communication//score/mw/com/impl:frontend_component)'
@score_communication//score/mw/com/dependability:mw_com_rst
@score_communication//score/mw/com/dependability:mw_com_index
@score_communication//score/mw/com/impl:frontend_component
```

```
$ bazel query 'kind(".*_test rule",
                    deps(@score_communication//score/mw/com/dependability:mw_com_rst))'
@score_communication//score/mw/com/impl:frontend_component
@score_communication//score/mw/com/impl/bindings:bindings
@score_communication//score/mw/com/impl/bindings/lola:lola_component
@score_communication//score/mw/com/impl/bindings/mock_binding:mock_component
@score_communication//third_party/score_baselibs:bitmanipulation
@score_communication//third_party/score_baselibs:bitmanipulation_component
@score_communication//third_party/score_baselibs:containers
@score_communication//third_party/score_baselibs:containers_component
@score_communication//third_party/score_baselibs:futurecpp
@score_communication//third_party/score_baselibs:futurecpp_component
@score_communication//third_party/score_baselibs:os
@score_communication//third_party/score_baselibs:os_component
```

The three paths, all in
[`eclipse-score/tooling`](https://github.com/eclipse-score/tooling/blob/main/bazel/rules/rules_score/private/dependable_element.bzl):

| Attribute of `_dependable_element_index` | Points at | Rule class | Read in the rule impl? |
|---|---|---|---|
| `components` (mandatory, line 1848) | `<x>_component` / `<x>` from the `component()` macro | `_component_test` (`component.bzl:359`) | yes, via aspect |
| `deps` (line 1875) | `<dep>` of other dependable elements | `_dependable_element_test` (`dependable_element.bzl:2036`, `test = True`) | only `dep.label.name`, line 693 |
| `tests` (line 1853) | real test targets (`message_passing` passes `//score/message_passing:unit_tests`) | `cc_test` etc. | **never** — no `ctx.attr.tests` anywhere |

Note the `components` row: `component()` creates its main target as a test rule
too, and `components` is a **mandatory** attribute of `dependable_element`. So
the contamination is structural, not just an artifact of the two optional
attributes.

## Possible directions

1. **`deps` and `tests` are cheap wins.** `ctx.attr.tests` is never read, and
   `ctx.attr.deps` is only used for `dep.label.name` in `_process_deps`
   (`dependable_element.bzl:693`) — no providers, no files. The real provider
   edge is `processed_deps` (`<dep>_index`, used at lines 1194/1369/1530).
   Making `deps` a `string_list` (or deriving the names from `processed_deps`)
   and dropping `tests` removes two of the three paths without any loss of
   functionality.

2. **`components` needs a split.** The documentation-producing part and the
   traceability-checking test would have to be separate targets, so that
   `<name>_index` can depend on the former without inheriting the latter. That
   is the same split that already exists for `<name>` vs `<name>_doc`.

3. **Or: give up on mounting and keep linking.** That is what
   eclipse-score/reference_integration#378 does.

## Context

* Linking PR: eclipse-score/reference_integration#378
* Rule source:
  `bazel/rules/rules_score/private/dependable_element.bzl` and
  `bazel/rules/rules_score/private/component.bzl` in `eclipse-score/tooling`
* Communication's dependable elements:
  `score/mw/com/dependability/BUILD`,
  `score/message_passing/dependability/BUILD`
