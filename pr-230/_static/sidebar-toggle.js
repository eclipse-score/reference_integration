/* *******************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 * *****************************************************************************/

(function () {
  "use strict";

  var STORAGE_KEY = "right-sidebar-collapsed";

  function init() {
    var sidebar = document.querySelector(".bd-sidebar-secondary");
    if (!sidebar) return;

    // Create toggle button
    var btn = document.createElement("button");
    btn.id = "right-sidebar-toggle";
    btn.title = "Toggle table of contents";
    btn.innerHTML = "&#x276F;"; // ❯
    sidebar.prepend(btn);

    // Restore persisted state
    if (localStorage.getItem(STORAGE_KEY) === "1") {
      sidebar.classList.add("collapsed");
      btn.innerHTML = "&#x276E;"; // ❮
    }

    btn.addEventListener("click", function () {
      var collapsed = sidebar.classList.toggle("collapsed");
      btn.innerHTML = collapsed ? "&#x276E;" : "&#x276F;";
      localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
