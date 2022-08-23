function getCurrentTheme() {
    if (document.cookie === "")
        return "default";

    return document.cookie
        .split('; ')
        .find(row => row.startsWith('theme='))
        .split('=')[1];
}

function toggleThemeSwitch() {
    let switchToggle = $(".switch")[0];
    let knob = $(".knob")[0];

    if (knob.classList.contains("dark")) {
        knob.classList.remove("dark");
        knob.classList.add("light");

        // After 500ms, switch the icons
        setTimeout(function() {
            switchToggle.classList.remove("dark");
            switchToggle.classList.add("light");
        }, 100);
    } else {
        knob.classList.remove("light");
        knob.classList.add("dark");

        // After 500ms, switch the icons
        setTimeout(function() {
            switchToggle.classList.remove("light");
            switchToggle.classList.add("dark");
        }, 100);
    }
}

// Executed when the page has finished loading.
document.addEventListener("DOMContentLoaded", () => {
    toggleThemeSwitch();

    $('#theme-switch').on("click", () => {

        // Update cookie
        if (getCurrentTheme() === "dark") {
            document.cookie = "theme=default";
        } else {
            document.cookie = "theme=dark";
        }

        toggleThemeSwitch();
        document.location.reload();
    });
});
