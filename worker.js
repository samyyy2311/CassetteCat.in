// /docs is served by Mintlify; everything else is the site's own files.
const DOCS_ORIGIN = "https://caffeinelabs.mintlify.site";
// Mintlify only answers for the domain it's set up with, so previews and workers.dev send this one too.
const SITE_HOST = "cassettecat.caffeinelabs.in";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    // The changelog became What's new; old links and search results still land on it.
    if (url.pathname === "/changelog" || url.pathname === "/changelog.html") {
      return Response.redirect(new URL("/whats-new" + url.search, url), 301);
    }
    if (url.pathname !== "/docs" && !url.pathname.startsWith("/docs/")) {
      return env.ASSETS.fetch(request);
    }
    const docsUrl = new URL(url.pathname + url.search, DOCS_ORIGIN);
    const docsRequest = new Request(docsUrl, request);
    docsRequest.headers.set("Host", docsUrl.hostname);
    docsRequest.headers.set("X-Forwarded-Host", SITE_HOST);
    docsRequest.headers.set("X-Forwarded-Proto", "https");
    return fetch(docsRequest);
  },
};
