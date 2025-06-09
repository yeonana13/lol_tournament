console.log('🎮 draft.js 로드 시작');

// 전역 변수
var draftSystem;

// DraftSystem 클래스
function DraftSystem(sessionId) {
    this.sessionId = sessionId;
    this.socket = io();
    this.champions = [];
    this.gameState = {
        currentTurn: 'blue_ban_1',
        timer: 30,
        bans: { blue: [], red: [] },
        picks: { blue: [], red: [] }
    };
    
    // LoL 공식 밴픽 순서
    this.draftOrder = [
        // 1라운드 밴 (3개씩)
        'blue_ban_1', 'red_ban_1', 'blue_ban_2', 'red_ban_2', 'blue_ban_3', 'red_ban_3',
        // 1라운드 픽 (3개씩, 교대로)
        'blue_pick_1', 'red_pick_1', 'red_pick_2', 'blue_pick_2', 'blue_pick_3', 'red_pick_3',
        // 2라운드 밴 (2개씩)
        'red_ban_4', 'blue_ban_4', 'red_ban_5', 'blue_ban_5',
        // 2라운드 픽 (2개씩)
        'red_pick_4', 'blue_pick_4', 'blue_pick_5', 'red_pick_5',
        'completed'
    ];
    
    this.currentTurnIndex = 0;
    this.timerInterval = null;
    
    console.log('🎮 DraftSystem 초기화 완료');
    this.initializeSocket();
    this.loadChampions();
    this.setupSearch();
    this.startTimer();
    this.updateCurrentTurnDisplay();
}

// 소켓 초기화
DraftSystem.prototype.initializeSocket = function() {
    var self = this;
    
    this.socket.on('connect', function() {
        console.log('🔌 드래프트 소켓 연결됨');
        self.socket.emit('join_draft', { session_id: self.sessionId });
    });

    this.socket.on('champion_selected', function(data) {
        console.log('📡 챔피언 선택 받음:', data);
        self.handleChampionSelection(data);
    });
};

// 챔피언 데이터 로드
DraftSystem.prototype.loadChampions = function() {
    var self = this;
    
    fetch('/api/session/' + this.sessionId)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            self.champions = data.champions;
            self.renderChampionGrid();
            console.log('📊 ' + self.champions.length + '개 챔피언 로드됨');
        })
        .catch(function(error) {
            console.error('챔피언 데이터 로드 실패:', error);
            self.createDummyChampions();
        });
};

// 더미 챔피언 데이터 생성
DraftSystem.prototype.createDummyChampions = function() {
    var dummyChampions = [
        '가렌', '갈리오', '갱플랭크', '그라가스', '그레이브즈', '그웬', '나르', '나미',
        '나서스', '노틸러스', '녹턴', '누누와 윌럼프', '니달리', '니코', '닐라', '다리우스',
        '다이애나', '드레이븐', '라이즈', '라칸', '람머스', '럭스', '럼블', '레나타 글라스크',
        '레넥톤', '레오나', '렉사이', '렐', '렝가', '루시안', '룰루', '르블랑', '리 신',
        '리븐', '리산드라', '릴리아', '마스터 이', '마오카이', '말자하', '말파이트', '모데카이저',
        '모르가나', '문도 박사', '미스 포츈', '바드', '바루스', '바이', '베이가', '베인',
        '벡스', '벨코즈', '볼리베어', '브라움', '브랜드', '브라이어', '블라디미르', '블리츠크랭크',
        '비에고', '빅토르', '뽀삐', '사미라', '사이온', '사일러스', '샤코', '세나',
        '세라핀', '세주아니', '세트', '소나', '소라카', '쉔', '쉬바나', '스웨인',
        '스카너', '시비르', '신 짜오', '신드라', '신지드', '쓰레쉬', '아리', '아무무',
        '아우렐리온 솔', '아이번', '아지르', '아칼리', '아크샨', '아트록스', '아펠리오스', '알리스타',
        '애니', '애니비아', '애쉬', '야스오', '얀디', '에코', '엘리스', '오공',
        '오른', '오리아나', '올라프', '요네', '요릭', '우디르', '우르곳', '워윅',
        '유미', '이렐리아', '이블린', '이즈리얼', '일라오이', '자르반 4세', '자야', '자이라',
        '자크', '잔나', '잭스', '제드', '제라스', '제리', '제이스', '조이', '직스',
        '진', '질리언', '징크스', '초가스', '카르마', '카밀', '카사딘', '카시오페아',
        '카타리나', '카이사', '카직스', '칼리스타', '케넨', '케이틀린', '케인', '케일',
        '코그모', '코르키', '퀸', '키아나', '킨드레드', '타릭', '탈론', '탈리야',
        '탐 켄치', '트런들', '트리스타나', '트린다미어', '트위스티드 페이트', '트위치', '티모', '파이크',
        '판테온', '피들스틱', '피오라', '피즈', '하이머딩거', '헤카림', '현'
    ];
    
    this.champions = [];
    for (var i = 0; i < dummyChampions.length; i++) {
        this.champions.push({
            id: i + 1,
            english_name: dummyChampions[i],
            korean_name: dummyChampions[i],
            image_url: 'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/' + dummyChampions[i] + '.png'
        });
    }
    
    this.renderChampionGrid();
    console.log('🧪 더미 챔피언 데이터 생성됨');
};

// 챔피언 그리드 렌더링
DraftSystem.prototype.renderChampionGrid = function() {
    var grid = document.getElementById('championGrid');
    grid.innerHTML = '';
    var self = this;

    for (var i = 0; i < this.champions.length; i++) {
        var champion = this.champions[i];
        var card = document.createElement('div');
        card.className = 'champion-card';
        card.setAttribute('data-champion', champion.english_name);
        card.setAttribute('data-search', champion.english_name.toLowerCase() + ' ' + champion.korean_name.toLowerCase());
        
        var isBanned = this.isChampionBanned(champion.korean_name);
        var isPicked = this.isChampionPicked(champion.korean_name);
        
        if (isBanned || isPicked) {
            card.classList.add('disabled');
        }

        card.innerHTML = '<img src="' + champion.image_url + '" alt="' + champion.korean_name + '" onerror="this.style.display=\'none\';" />' +
                        '<div class="name">' + champion.korean_name + '</div>' +
                        (isBanned ? '<div class="ban-indicator">🚫</div>' : '');

        if (!isBanned && !isPicked) {
            card.onclick = (function(englishName, koreanName) {
                return function() {
                    self.selectChampion(englishName, koreanName);
                };
            })(champion.english_name, champion.korean_name);
        }

        grid.appendChild(card);
    }
};

// 챔피언 선택
DraftSystem.prototype.selectChampion = function(englishName, koreanName) {
    var currentAction = this.getCurrentAction();
    if (!currentAction) {
        console.log('❌ 현재 유효한 턴이 아닙니다');
        return;
    }

    console.log('🎯 챔피언 선택: ' + koreanName + ' (' + currentAction.action + ')');

    // 로컬에서 먼저 업데이트
    if (currentAction.action === 'ban') {
        this.gameState.bans[currentAction.team].push(koreanName);
    } else if (currentAction.action === 'pick') {
        this.gameState.picks[currentAction.team].push(koreanName);
    }

    this.socket.emit('select_champion', {
        session_id: this.sessionId,
        champion_english: englishName,
        champion_korean: koreanName,
        action: currentAction.action,
        team: currentAction.team,
        turn: this.gameState.currentTurn
    });

    this.nextTurn();
    this.renderChampionGrid();
    this.updateBanPickDisplay();
};

// 현재 액션 가져오기
DraftSystem.prototype.getCurrentAction = function() {
    var turn = this.gameState.currentTurn;
    if (turn === 'completed') return null;
    
    if (turn.indexOf('ban') !== -1) {
        return {
            action: 'ban',
            team: turn.indexOf('blue') !== -1 ? 'blue' : 'red'
        };
    } else if (turn.indexOf('pick') !== -1) {
        return {
            action: 'pick',
            team: turn.indexOf('blue') !== -1 ? 'blue' : 'red'
        };
    }
    return null;
};

// 다음 턴
DraftSystem.prototype.nextTurn = function() {
    this.currentTurnIndex++;
    if (this.currentTurnIndex < this.draftOrder.length) {
        this.gameState.currentTurn = this.draftOrder[this.currentTurnIndex];
        this.gameState.timer = 30;
        this.updateCurrentTurnDisplay();
        this.resetTimer();
    } else {
        this.completeDraft();
    }
};

// 드래프트 완료
DraftSystem.prototype.completeDraft = function() {
    this.gameState.currentTurn = 'completed';
    this.stopTimer();
    
    document.getElementById('currentTurn').textContent = '🎉 밴픽 완료!';
    document.getElementById('timer').textContent = '✅';
    document.getElementById('timer').className = 'timer';
    
    console.log('🎉 밴픽 드래프트 완료!');
    console.log('최종 결과:', this.gameState);
};

// 현재 턴 표시 업데이트
DraftSystem.prototype.updateCurrentTurnDisplay = function() {
    var turnElement = document.getElementById('currentTurn');
    var turn = this.gameState.currentTurn;
    
    var turnDescriptions = {
        // 1라운드 밴 (3개씩)
        'blue_ban_1': '블루팀 1밴',
        'red_ban_1': '레드팀 1밴',
        'blue_ban_2': '블루팀 2밴',
        'red_ban_2': '레드팀 2밴',
        'blue_ban_3': '블루팀 3밴',
        'red_ban_3': '레드팀 3밴',
        // 1라운드 픽 (3개씩)
        'blue_pick_1': '블루팀 1픽',
        'red_pick_1': '레드팀 1픽',
        'red_pick_2': '레드팀 2픽',
        'blue_pick_2': '블루팀 2픽',
        'blue_pick_3': '블루팀 3픽',
        'red_pick_3': '레드팀 3픽',
        // 2라운드 밴 (2개씩)
        'red_ban_4': '레드팀 4밴',
        'blue_ban_4': '블루팀 4밴',
        'red_ban_5': '레드팀 5밴',
        'blue_ban_5': '블루팀 5밴',
        // 2라운드 픽 (2개씩)
        'red_pick_4': '레드팀 4픽',
        'blue_pick_4': '블루팀 4픽',
        'blue_pick_5': '블루팀 5픽',
        'red_pick_5': '레드팀 5픽'
    };
    
    turnElement.textContent = turnDescriptions[turn] || turn;
};

// 밴픽 표시 업데이트
DraftSystem.prototype.updateBanPickDisplay = function() {
    var self = this;
    
    // 밴 표시 업데이트
    ['blue', 'red'].forEach(function(team) {
        var banSlots = document.querySelectorAll('#' + team + 'Bans .champion-slot');
        var bans = self.gameState.bans[team];
        
        for (var i = 0; i < banSlots.length; i++) {
            if (bans[i]) {
                var champion = null;
                for (var j = 0; j < self.champions.length; j++) {
                    if (self.champions[j].korean_name === bans[i]) {
                        champion = self.champions[j];
                        break;
                    }
                }
                banSlots[i].innerHTML = '<img src="' + (champion ? champion.image_url : '') + '" alt="' + bans[i] + '" onerror="this.style.display=\'none\';" />' +
                                       '<div class="ban-overlay">🚫</div>';
            }
        }
    });

    // 픽 표시 업데이트
    ['blue', 'red'].forEach(function(team) {
        var pickSlots = document.querySelectorAll('#' + team + 'Picks .pick-slot');
        var picks = self.gameState.picks[team];
        
        for (var i = 0; i < pickSlots.length; i++) {
            if (picks[i]) {
                pickSlots[i].classList.add('filled');
                pickSlots[i].querySelector('.champion-name').textContent = picks[i];
            } else {
                pickSlots[i].classList.remove('filled');
                pickSlots[i].querySelector('.champion-name').textContent = '-';
            }
        }
    });
};

// 챔피언 밴 여부 확인
DraftSystem.prototype.isChampionBanned = function(koreanName) {
    return this.gameState.bans.blue.indexOf(koreanName) !== -1 ||
           this.gameState.bans.red.indexOf(koreanName) !== -1;
};

// 챔피언 픽 여부 확인
DraftSystem.prototype.isChampionPicked = function(koreanName) {
    return this.gameState.picks.blue.indexOf(koreanName) !== -1 ||
           this.gameState.picks.red.indexOf(koreanName) !== -1;
};

// 검색 기능 설정
DraftSystem.prototype.setupSearch = function() {
    var searchBox = document.getElementById('championSearch');
    searchBox.addEventListener('input', function(e) {
        var query = e.target.value.toLowerCase();
        var cards = document.querySelectorAll('.champion-card');
        
        for (var i = 0; i < cards.length; i++) {
            var searchText = cards[i].getAttribute('data-search');
            if (searchText && searchText.indexOf(query) !== -1) {
                cards[i].style.display = 'block';
            } else {
                cards[i].style.display = 'none';
            }
        }
    });
};

// 타이머 시작
DraftSystem.prototype.startTimer = function() {
    this.resetTimer();
};

// 타이머 리셋
DraftSystem.prototype.resetTimer = function() {
    this.stopTimer();
    this.gameState.timer = 30;
    this.updateTimerDisplay();
    var self = this;
    
    this.timerInterval = setInterval(function() {
        self.gameState.timer--;
        self.updateTimerDisplay();
        
        if (self.gameState.timer <= 0) {
            self.handleTimeOut();
        }
    }, 1000);
};

// 타이머 정지
DraftSystem.prototype.stopTimer = function() {
    if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
    }
};

// 타이머 표시 업데이트
DraftSystem.prototype.updateTimerDisplay = function() {
    var timerElement = document.getElementById('timer');
    timerElement.textContent = this.gameState.timer;
    
    // 타이머 색상 변경
    timerElement.className = 'timer';
    if (this.gameState.timer <= 5) {
        timerElement.classList.add('danger');
    } else if (this.gameState.timer <= 10) {
        timerElement.classList.add('warning');
    }
};

// 시간 초과 처리
DraftSystem.prototype.handleTimeOut = function() {
    console.log('⏰ 시간 초과! 자동으로 다음 턴');
    this.stopTimer();
    this.nextTurn();
    this.renderChampionGrid();
    this.updateBanPickDisplay();
};

// 챔피언 선택 처리 (소켓용)
DraftSystem.prototype.handleChampionSelection = function(data) {
    console.log('📡 챔피언 선택 업데이트:', data);
    // 서버에서 온 데이터로 상태 동기화 (필요한 경우)
};

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    var sessionId = document.querySelector('[data-session-id]').dataset.sessionId;
    draftSystem = new DraftSystem(sessionId);
    console.log('🚀 드래프트 시스템 초기화 완료');
});
