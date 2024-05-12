$(document).ready(function () {
    // Close notification
    $('.notification .delete').click(function () {
        $(this).parent().fadeOut(() => $(this).remove());
    });

    // Navbar Burger Script
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
    if ($navbarBurgers.length > 0) {
        $navbarBurgers.forEach(function ($el) {
            $el.addEventListener('click', function () {
                const target = $el.dataset.target;
                const $target = document.getElementById(target);
                $el.classList.toggle('is-active');
                $target.classList.toggle('is-active');
            });
        });
    }

    // Navbar Dropdown Script
    const $dropdowns = Array.prototype.slice.call(document.querySelectorAll('.navbar-item.has-dropdown'), 0);
    if ($dropdowns.length > 0) {
        $dropdowns.forEach(function ($el) {
            $el.querySelector('.navbar-link').addEventListener('click', function (event) {
                event.preventDefault();
                $el.classList.toggle('is-active');
            });
        });
    }

    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const toggleIcon = sidebarToggle.querySelector('.icon i');

    function updateSidebarState(isVisible) {
        localStorage.setItem('sidebarIsVisible', isVisible ? 'true' : 'false');
    }

    const sidebarIsVisible = localStorage.getItem('sidebarIsVisible') === 'true';

    // Temporarily disable CSS transitions
    sidebar.style.transition = 'none';
    content.style.transition = 'none';

    if (sidebarIsVisible) {
        sidebar.classList.add('is-visible');
        toggleIcon.classList.add('fa-chevron-left');
        toggleIcon.classList.remove('fa-chevron-right');
        content.classList.add('sidebar-is-visible');
        content.style.marginLeft = '250px';
    } else {
        sidebar.classList.remove('is-visible');
        toggleIcon.classList.add('fa-chevron-right');
        toggleIcon.classList.remove('fa-chevron-left');
        content.classList.remove('sidebar-is-visible');
        content.style.marginLeft = '0';
    }

    setTimeout(() => {
        sidebar.style.transition = '';
        content.style.transition = '';
    }, 0);

    sidebarToggle.onclick = function () {
        sidebar.classList.toggle('is-visible');
        toggleIcon.classList.toggle('fa-chevron-right');
        toggleIcon.classList.toggle('fa-chevron-left');
        content.classList.toggle('sidebar-is-visible');

        const isVisible = sidebar.classList.contains('is-visible');
        updateSidebarState(isVisible);

        content.style.marginLeft = isVisible ? '250px' : '0';
    };
});
