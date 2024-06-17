const cardsContainer        =   document.querySelector('.container');

cardsContainer.addEventListener('click', (e) => {
    const target            =   e.target.closest('.card');

    if (!target) return;

    cardsContainer.querySelectorAll('.card').forEach((card) => {
        card.classList.remove('active');
    });

    target.classList.add('active');
});

// Redirecionamentos //
const divBoutMe             =   document.getElementById('aboutMe');
divBoutMe.addEventListener("click", () =>{
    window.location.href    =   '/sobre-mim.html';
});

const divMyIG               =   document.getElementById('myIG');
divMyIG.addEventListener("click", () =>{
    window.location.href    =   'https://instagram.com/caioyurilopes';
});
// ----------------- //