 
(() => {
	function getTheme() {
		const root = document.documentElement;
		return (root.getAttribute("data-theme") || "light").toLowerCase();
	}

	function updateNavbarLogo(theme) {
		const logoEl = document.querySelector("header .app-logo");
		if (!logoEl) return;
		const lightLogo = "/assets/climoro_onboarding/images/Climoro.png";
		const darkLogo = "/files/climoro%20logo%20blackbg.png";
		const desired = theme === "dark" ? darkLogo : lightLogo;
		if (logoEl.getAttribute("src") !== desired) {
			logoEl.setAttribute("src", desired);
			logoEl.setAttribute("alt", "Climoro Logo");
		}
	}

	function updateSplash(theme) {
		const splashImg = document.querySelector(".splash img");
		if (!splashImg) return;
		const lightSplash = "/assets/climoro_onboarding/images/Climoro.png";
		const darkSplash = "/files/climoro%20logo%20blackbg.png";
		const desired = theme === "dark" ? darkSplash : lightSplash;
		if (splashImg.getAttribute("src") !== desired) {
			splashImg.setAttribute("src", desired);
			splashImg.setAttribute("alt", "Climoro Splash");
		}
	}

	function updateFavicon(theme) {
		// prefer small icons if you have them; using logos as fallback
		const lightIcon = "/assets/climoro_onboarding/images/Climoro.png";
		const darkIcon = "/files/climoro%20logo%20blackbg.png";
		const href = theme === "dark" ? darkIcon : lightIcon;

		// Remove existing, then add back like Frappe does
		const existing = document.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]');
		existing.forEach((el) => el.parentNode && el.parentNode.removeChild(el));
		const link1 = document.createElement("link");
		link1.rel = "shortcut icon";
		link1.type = "image/x-icon";
		link1.href = href;
		document.head.appendChild(link1);
		const link2 = document.createElement("link");
		link2.rel = "icon";
		link2.type = "image/x-icon";
		link2.href = href;
		document.head.appendChild(link2);
	}

	function applyBranding() {
		const theme = getTheme();
		updateNavbarLogo(theme);
		updateSplash(theme);
		updateFavicon(theme);
	}

	function init() {
		applyBranding();
		// React to theme toggles
		const root = document.documentElement;
		new MutationObserver(applyBranding).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
		// Navbar re-render hooks
		document.addEventListener("toolbar_setup", applyBranding);
		document.addEventListener("app_ready", applyBranding);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();

(() => {
	function getTheme() {
		const root = document.documentElement;
		// Frappe sets data-theme to "light" or "dark"
		return (root.getAttribute("data-theme") || "light").toLowerCase();
	}

	function setNavbarLogo() {
		const logoEl = document.querySelector("header .app-logo");
		if (!logoEl) return;

		const theme = getTheme();
		// Light theme → colored logo; Dark theme → light logo for dark bg
		const lightLogo = "/assets/climoro_onboarding/images/Climoro.png";
		const darkLogo = "/files/climoro%20logo%20blackbg.png";

		const desired = theme === "dark" ? darkLogo : lightLogo;
		if (logoEl.getAttribute("src") !== desired) {
			logoEl.setAttribute("src", desired);
			logoEl.setAttribute("alt", "Climoro Logo");
		}
	}

	function init() {
		// Run once when desk renders
		setNavbarLogo();

		// Update whenever theme changes (Frappe updates data-theme)
		const root = document.documentElement;
		const observer = new MutationObserver(() => setNavbarLogo());
		observer.observe(root, { attributes: true, attributeFilter: ["data-theme"] });

		// Also when navbar is re-rendered on boot or route changes
		document.addEventListener("app_ready", setNavbarLogo);
		document.addEventListener("toolbar_setup", setNavbarLogo);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
