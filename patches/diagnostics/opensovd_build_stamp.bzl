# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""Generate reproducible OpenSOVD build metadata from the pinned commit."""

def timestamp_to_epoch(timestamp):
    """Convert a GitHub UTC commit timestamp to a Unix timestamp."""

    # GitHub's Git commit API returns UTC timestamps in this exact format.
    if len(timestamp) != 20 or timestamp[4] != "-" or timestamp[7] != "-" or timestamp[10] != "T" or timestamp[13] != ":" or timestamp[16] != ":" or timestamp[19] != "Z":
        fail("Invalid UTC commit timestamp: %s" % timestamp)
    digits = timestamp[0:4] + timestamp[5:7] + timestamp[8:10] + timestamp[11:13] + timestamp[14:16] + timestamp[17:19]
    if any([c not in "0123456789" for c in digits.elems()]):
        fail("Invalid UTC commit timestamp: %s" % timestamp)
    year = int(timestamp[0:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    hour = int(timestamp[11:13])
    minute = int(timestamp[14:16])
    second = int(timestamp[17:19])
    if year < 1970 or month < 1 or month > 12 or hour > 23 or minute > 59 or second > 59:
        fail("Invalid UTC commit timestamp: %s" % timestamp)
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if day < 1 or day > month_days[month - 1]:
        fail("Invalid UTC commit timestamp: %s" % timestamp)
    previous_year = year - 1
    days = 365 * (year - 1970) + previous_year // 4 - previous_year // 100 + previous_year // 400 - (1969 // 4 - 1969 // 100 + 1969 // 400)
    for month_length in month_days[:month - 1]:
        days += month_length
    days += day - 1
    return ((days * 24 + hour) * 60 + minute) * 60 + second

def _opensovd_build_stamp_impl(rctx):
    commit = rctx.attr.commit
    if len(commit) != 40 or any([c not in "0123456789abcdef" for c in commit.elems()]):
        fail("OpenSOVD commit must be a full lowercase Git SHA: %s" % commit)

    # Git metadata is unavailable to sandboxed build scripts. Resolve the
    # immutable commit once at repository fetch time, then declare the result
    # as a normal build input. This requires access to the GitHub API on a
    # cold repository cache, in addition to fetching the OpenSOVD source.
    rctx.download(
        url = "https://api.github.com/repos/eclipse-opensovd/opensovd-core/git/commits/" + commit,
        output = "commit.json",
    )
    metadata = json.decode(rctx.read("commit.json"))
    if metadata.get("sha") != commit:
        fail("OpenSOVD commit metadata does not match %s" % commit)
    timestamp = metadata["committer"]["date"]
    epoch = timestamp_to_epoch(timestamp)
    rctx.file("stamp.env", "OPENSOVD_COMMIT_SHA=%s\nSOURCE_DATE_EPOCH=%s\n" % (commit, epoch))
    rctx.file("commit_date.txt", timestamp[:10] + "\n")
    rctx.file("BUILD.bazel", "exports_files([\"stamp.env\", \"commit_date.txt\"], visibility = [\"//visibility:public\"])\n")

opensovd_build_stamp = repository_rule(
    implementation = _opensovd_build_stamp_impl,
    attrs = {"commit": attr.string(mandatory = True)},
)
