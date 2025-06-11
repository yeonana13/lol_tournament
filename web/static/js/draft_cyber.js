console.log('🎮 Cyber Draft System 로드 시작');

// CyberDraftSystem 클래스
class CyberDraftSystem {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.socket = io();
        this.champions = [];
        this.participants = [];
        this.currentTurnIndex = 0;
        this.timerInterval = null;
        this.timeLeft = 30;
        this.selectedChampion = null;
        
        // LoL 공식 밴픽 순서 (TOP이 밴 담당)
        this.draftOrder = [
            // 1라운드 밴
            { team: 'blue', action: 'ban', position: 'TOP', display: '🔵 블루팀 1번째 밴' },
            { team: 'red', action: 'ban', position: 'TOP', display: '🔴 레드팀 1번째 밴' },
            { team: 'blue', action: 'ban', position: 'TOP', display: '🔵 블루팀 2번째 밴' },
            { team: 'red', action: 'ban', position: 'TOP', display: '🔴 레드팀 2번째 밴' },
            { team: 'blue', action: 'ban', position: 'TOP', display: '🔵 블루팀 3번째 밴' },
            { team: 'red', action: 'ban', position: 'TOP', display: '🔴 레드팀 3번째 밴' },
            
            // 1라운드 픽
            { team: 'blue', action: 'pick', position: 'TOP', display: '🔵 블루팀 TOP 픽' },
            { team: 'red', action: 'pick', position: 'TOP', display: '🔴 레드팀 TOP 픽' },
            { team: 'red', action: 'pick', position: 'JUG', display: '🔴 레드팀 정글 픽' },
            { team: 'blue', action: 'pick', position: 'JUG', display: '🔵 블루팀 정글 픽' },
            { team: 'blue', action: 'pick', position: 'MID', display: '🔵 블루팀 미드 픽' },
            { team: 'red', action: 'pick', position: 'MID', display: '🔴 레드팀 미드 픽' },
            
            // 2라운드 밴
            { team: 'red', action: 'ban', position: 'TOP', display: '🔴 레드팀 4번째 밴' },
            { team: 'blue', action: 'ban', position: 'TOP', display: '🔵 블루팀 4번째 밴' },
            { team: 'red', action: 'ban', position: 'TOP', display: '🔴 레드팀 5번째 밴' },
            { team: 'blue', action: 'ban', position: 'TOP', display: '🔵 블루팀 5번째 밴' },
            
            // 2라운드 픽
            { team: 'red', action: 'pick', position: 'ADC', display: '🔴 레드팀 원딜 픽' },
            { team: 'blue', action: 'pick', position: 'ADC', display: '🔵 블루팀 원딜 픽' },
            { team: 'blue', action: 'pick', position: 'SUP', display: '🔵 블루팀 서폿 픽' },
            { team: 'red', action: 'pick', position: 'SUP', display: '🔴 레드팀 서폿 픽' }
        ];
        
        this.gameState = {
            bans: { blue: [], red: [] },
            picks: { blue: [], red: [] },
            teams: {
                blue: { TOP: null, JUG: null, MID: null, ADC: null, SUP: null },
                red: { TOP: null, JUG: null, MID: null, ADC: null, SUP: null }
            }
        };
        
        console.log('🎮 CyberDraftSystem 초기화 완료');
        this.initialize();
    }
    
    async initialize() {
        try {
            await this.initializeSocket();
            await this.loadChampions();
            await this.loadParticipants();
            this.setupEventListeners();
            this.renderTeamSlots();
            this.updateCurrentTurn();
            this.startTimer();
            
            console.log('✅ 시스템 초기화 완료');
        } catch (error) {
            console.error('❌ 초기화 실패:', error);
            this.showError('시스템 초기화에 실패했습니다.');
        }
    }
    
    initializeSocket() {
        return new Promise((resolve) => {
            this.socket.on('connect', () => {
                console.log('🔌 소켓 연결됨');
                this.socket.emit('join_session', { 
                    session_id: this.sessionId,
                    discord_id: this.getCurrentUserDiscordId()
                });
                resolve();
            });
            
            this.socket.on('disconnect', () => {
                console.log('🔌 소켓 연결 해제');
                this.showError('서버와의 연결이 끊어졌습니다.');
            });
            
            this.socket.on('game_state_update', (data) => {
                console.log('🎮 게임 상태 업데이트:', data);
                if (data.participants) {
                    this.participants = data.participants;
                    this.renderTeamSlots();
                }
                if (data.game_state) {
                    this.updateFromGameState(data.game_state);
                }
            });
            
            this.socket.on('champion_selected', (data) => {
                console.log('🎯 챔피언 선택됨:', data);
                this.handleRemoteChampionSelection(data);
            });
            
            this.socket.on('draft_completed', () => {
                console.log('🎉 드래프트 완료!');
                this.showDraftCompleted();
            });
            
            this.socket.on('error', (error) => {
                console.error('🚨 소켓 에러:', error);
                this.showError('통신 오류가 발생했습니다.');
            });
        });
    }
    
    async loadChampions() {
        try {
            console.log('📊 챔피언 데이터 로딩 시작...');
            const response = await fetch(`/api/session/${this.sessionId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.champions = data.champions || [];
            
            if (this.champions.length === 0) {
                console.warn('⚠️ 챔피언 데이터가 없어 더미 데이터 로드');
                this.loadDummyChampions();
            } else {
                this.renderChampionGrid();
                console.log('✅ 챔피언 데이터 로드 완료:', this.champions.length + '개');
            }
        } catch (error) {
            console.error('❌ 챔피언 로드 실패:', error);
            this.loadDummyChampions();
        }
    }
    
    async loadParticipants() {
        try {
            console.log('👥 참가자 데이터 로딩 시작...');
            const response = await fetch(`/api/session/${this.sessionId}/users`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.participants = data.participants || [];
            
            if (this.participants.length === 0) {
                console.warn('⚠️ 참가자 데이터가 없어 더미 데이터 로드');
                this.loadDummyParticipants();
            } else {
                console.log('✅ 참가자 데이터 로드 완료:', this.participants.length + '명');
            }
        } catch (error) {
            console.error('❌ 참가자 로드 실패:', error);
            this.loadDummyParticipants();
        }
    }
    
    loadDummyChampions() {
        const dummyChampions = [
            'Aatrox', 'Ahri', 'Akali', 'Alistar', 'Amumu', 'Anivia', 'Annie', 'Ashe',
            'Blitzcrank', 'Brand', 'Braum', 'Caitlyn', 'Darius', 'Diana', 'Draven',
            'Ezreal', 'Fiora', 'Garen', 'Graves', 'Janna', 'Jarvan', 'Jax', 'Jinx',
            'Katarina', 'Lux', 'Malphite', 'Nasus', 'Orianna', 'Riven', 'Thresh',
            'Vayne', 'Yasuo', 'Zed', 'Zyra', 'LeeSin', 'Syndra', 'Azir', 'Kalista',
            'Ekko', 'Tahm', 'Kindred', 'Jhin', 'Aurelion', 'Taliyah', 'Camille'
        ];
        
        this.champions = dummyChampions.map(name => ({
            english_name: name,
            korean_name: name,
            image_url: `https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/${name}.png`
        }));
        
        this.renderChampionGrid();
        console.log('🧪 더미 챔피언 데이터 로드 완료:', this.champions.length + '개');
    }
    
    loadDummyParticipants() {
        this.participants = [];
        for (let i = 0; i < 10; i++) {
            this.participants.push({
                discord_id: `dummy_${i}`,
                username: `TestUser${i + 1}`,
                display_name: `테스트유저${i + 1}`,
                avatar_url: `https://cdn.discordapp.com/embed/avatars/${i % 6}.png`
            });
        }
        console.log('🧪 더미 참가자 데이터 로드 완료:', this.participants.length + '명');
    }
    
    renderTeamSlots() {
        const positions = ['TOP', 'JUG', 'MID', 'ADC', 'SUP'];
        
        this.renderTeam('blue', positions, document.getElementById('blueTeamSlots'), 0);
        this.renderTeam('red', positions, document.getElementById('redTeamSlots'), 5);
    }
    
    renderTeam(teamColor, positions, container, offset) {
        container.innerHTML = '';
        
        positions.forEach((position, index) => {
            const participant = this.participants[offset + index] || null;
            const championPick = this.gameState.teams[teamColor][position];
            
            const slotEl = document.createElement('div');
            slotEl.className = 'position-slot';
            slotEl.dataset.team = teamColor;
            slotEl.dataset.position = position;
            
            slotEl.innerHTML = `
                <div class="position-label">${position}</div>
                <div class="player-info">
                    <img src="${participant?.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                         alt="${position}" class="player-avatar"
                         onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                    <div class="player-name">${participant?.display_name || '대기 중'}</div>
                </div>
                <div class="champion-pick">
                    ${championPick ? 
                        `<img src="${championPick.image_url}" alt="${championPick.korean_name}" class="champion-icon"
                              onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">` : 
                        '<span>?</span>'
                    }
                </div>
            `;
            
            container.appendChild(slotEl);
        });
    }
    
    renderChampionGrid() {
        const gridEl = document.getElementById('championGrid');
        if (!gridEl) {
            console.error('❌ championGrid 요소를 찾을 수 없습니다.');
            return;
        }
        
        gridEl.innerHTML = '';
        
        this.champions.forEach(champion => {
            const itemEl = document.createElement('div');
            itemEl.className = 'champion-item';
            itemEl.dataset.championId = champion.english_name;
            itemEl.dataset.championKorean = champion.korean_name;
            
            // 밴/픽 상태 체크
            const isBanned = this.isChampionBanned(champion.korean_name);
            const isPicked = this.isChampionPicked(champion.korean_name);
            
            if (isBanned) itemEl.classList.add('banned');
            if (isPicked) itemEl.classList.add('picked');
            
            itemEl.innerHTML = `
                <img src="${champion.image_url}" alt="${champion.korean_name}"
                     onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
            `;
            
            if (!isBanned && !isPicked) {
                itemEl.addEventListener('click', () => this.selectChampion(champion));
            }
            
            gridEl.appendChild(itemEl);
        });
    }
    
    isChampionBanned(championName) {
        return this.gameState.bans.blue.includes(championName) || 
               this.gameState.bans.red.includes(championName);
    }
    
    isChampionPicked(championName) {
        return this.gameState.picks.blue.includes(championName) || 
               this.gameState.picks.red.includes(championName);
    }
    
    selectChampion(champion) {
        if (this.isChampionBanned(champion.korean_name) || this.isChampionPicked(champion.korean_name)) {
            return;
        }
        
        // 기존 선택 제거
        document.querySelectorAll('.champion-item.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // 새로운 선택
        const itemEl = document.querySelector(`[data-champion-id="${champion.english_name}"]`);
        if (itemEl) {
            itemEl.classList.add('selected');
        }
        
        this.selectedChampion = champion;
        
        // 액션 버튼 활성화
        const actionBtn = document.getElementById('actionBtn');
        if (actionBtn) {
            actionBtn.disabled = false;
        }
        
        console.log('🎯 챔피언 선택:', champion.korean_name);
    }
    
    updateCurrentTurn() {
        if (this.currentTurnIndex >= this.draftOrder.length) {
            this.showDraftCompleted();
            return;
        }
        
        const currentTurn = this.draftOrder[this.currentTurnIndex];
        
        // 현재 턴 표시 업데이트
        this.updateTurnDisplay(currentTurn);
        
        // 액션 버튼 업데이트
        this.updateActionButton(currentTurn);
        
        // 포지션 하이라이트
        this.highlightCurrentPosition(currentTurn);
        
        // 타이머 리셋
        this.timeLeft = 30;
        
        console.log('🔄 턴 업데이트:', currentTurn);
    }
    
    updateTurnDisplay(currentTurn) {
        const turnAvatar = document.getElementById('turnAvatar');
        const turnInfo = document.getElementById('turnInfo');
        
        // 현재 턴 플레이어 찾기
        const currentPlayer = this.getCurrentTurnPlayer(currentTurn);
        
        if (currentPlayer && turnAvatar && turnInfo) {
            turnAvatar.src = currentPlayer.avatar_url;
            turnAvatar.onerror = () => {
                turnAvatar.src = 'https://cdn.discordapp.com/embed/avatars/0.png';
            };
            
            turnInfo.innerHTML = `
                <div>${currentPlayer.display_name}님의 턴 ${currentTurn.action === 'ban' ? '(TOP)' : ''}</div>
                <div>${currentTurn.display}</div>
            `;
        }
    }
    
    updateActionButton(currentTurn) {
        const actionBtn = document.getElementById('actionBtn');
        if (!actionBtn) return;
        
        if (currentTurn.action === 'ban') {
            actionBtn.textContent = '⛔ 밴하기';
            actionBtn.className = 'current-action-btn ban-mode';
        } else {
            actionBtn.textContent = '✅ 픽하기';
            actionBtn.className = 'current-action-btn pick-mode';
        }
        actionBtn.disabled = true;
    }
    
    getCurrentTurnPlayer(currentTurn) {
        const positions = ['TOP', 'JUG', 'MID', 'ADC', 'SUP'];
        const positionIndex = positions.indexOf(currentTurn.position);
        const teamOffset = currentTurn.team === 'blue' ? 0 : 5;
        
        return this.participants[teamOffset + positionIndex] || null;
    }
    
    highlightCurrentPosition(currentTurn) {
        // 모든 하이라이트 제거
        document.querySelectorAll('.position-slot').forEach(slot => {
            slot.classList.remove('current-pick');
        });
        
        // 현재 포지션 하이라이트
        const targetSlot = document.querySelector(
            `[data-team="${currentTurn.team}"][data-position="${currentTurn.position}"]`
        );
        
        if (targetSlot) {
            targetSlot.classList.add('current-pick');
        }
    }
    
    executeAction() {
        if (!this.selectedChampion) {
            this.showError('챔피언을 선택해주세요.');
            return;
        }
        
        const currentTurn = this.draftOrder[this.currentTurnIndex];
        const championData = {
            english_name: this.selectedChampion.english_name,
            korean_name: this.selectedChampion.korean_name,
            image_url: this.selectedChampion.image_url
        };
        
        if (currentTurn.action === 'ban') {
            this.executeBan(currentTurn, championData);
        } else {
            this.executePick(currentTurn, championData);
        }
        
        // 소켓으로 전송
        this.socket.emit('select_champion', {
            session_id: this.sessionId,
            champion_english: championData.english_name,
            champion_korean: championData.korean_name,
            action: currentTurn.action,
            team: currentTurn.team,
            turn: this.currentTurnIndex
        });
        
        // 다음 턴으로
        this.currentTurnIndex++;
        this.selectedChampion = null;
        
        // UI 업데이트
        this.clearSelection();
        this.renderChampionGrid();
        this.updateCurrentTurn();
    }
    
    executeBan(currentTurn, championData) {
        this.gameState.bans[currentTurn.team].push(championData.korean_name);
        
        // 밴 슬롯에 추가
        const banSlotsId = currentTurn.team === 'blue' ? 'blueBanSlots' : 'redBanSlots';
        const banSlots = document.getElementById(banSlotsId);
        const emptySlot = banSlots?.querySelector('.ban-slot:not(.filled)');
        
        if (emptySlot) {
            emptySlot.innerHTML = `<img src="${championData.image_url}" alt="${championData.korean_name}"
                                        onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">`;
            emptySlot.classList.add('filled');
        }
        
        console.log(`⛔ ${currentTurn.team} 팀이 ${championData.korean_name}을(를) 밴했습니다.`);
    }
    
    executePick(currentTurn, championData) {
        this.gameState.picks[currentTurn.team].push(championData.korean_name);
        this.gameState.teams[currentTurn.team][currentTurn.position] = championData;
        
        // 팀 슬롯 업데이트
        this.renderTeamSlots();
        
        console.log(`✅ ${currentTurn.team} 팀 ${currentTurn.position}이(가) ${championData.korean_name}을(를) 픽했습니다.`);
    }
    
    clearSelection() {
        document.querySelectorAll('.champion-item.selected').forEach(el => {
            el.classList.remove('selected');
        });
    }
    
    setupEventListeners() {
        // 액션 버튼
        const actionBtn = document.getElementById('actionBtn');
        if (actionBtn) {
            actionBtn.addEventListener('click', () => {
                this.executeAction();
            });
        }
        
        // 챔피언 검색
        const searchInput = document.getElementById('championSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterChampions(e.target.value);
            });
        }
        
        // 키보드 단축키
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && this.selectedChampion) {
                this.executeAction();
            } else if (e.key === 'Escape') {
                this.clearSelection();
                const actionBtn = document.getElementById('actionBtn');
                if (actionBtn) actionBtn.disabled = true;
            }
        });
    }
    
    filterChampions(searchTerm) {
        const items = document.querySelectorAll('.champion-item');
        const term = searchTerm.toLowerCase();
        
        items.forEach(item => {
            const championName = item.querySelector('img')?.alt?.toLowerCase() || '';
            const championKorean = item.dataset.championKorean?.toLowerCase() || '';
            
            if (championName.includes(term) || championKorean.includes(term)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    startTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            
            const timerEl = document.getElementById('timer');
            if (timerEl) {
                timerEl.textContent = this.timeLeft;
                
                if (this.timeLeft <= 10) {
                    timerEl.style.color = '#FF0066';
                } else {
                    timerEl.style.color = '#00FF88';
                }
            }
            
            if (this.timeLeft <= 0) {
                this.handleTimeOut();
            }
        }, 1000);
    }
    
    handleTimeOut() {
        console.log('⏰ 시간 초과');
        this.timeLeft = 30; // 리셋
        
        // 실제로는 자동 스킵 또는 랜덤 선택 처리
        // 여기서는 단순히 타이머만 리셋
    }
    
    showDraftCompleted() {
        const turnInfo = document.getElementById('turnInfo');
        if (turnInfo) {
            turnInfo.innerHTML = `
                <div>🎉 드래프트 완료!</div>
                <div>최종 확인 단계</div>
            `;
        }
        
        const actionBtn = document.getElementById('actionBtn');
        if (actionBtn) {
            actionBtn.style.display = 'none';
        }
        
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        console.log('🎉 드래프트가 완료되었습니다!');
        
        // 최종 결과 처리 로직 추가 예정
        this.showFinalResults();
    }
    
    showFinalResults() {
        // 최종 결과 표시 (추후 구현)
        setTimeout(() => {
            alert('드래프트가 완료되었습니다! 최종 확인 페이지로 이동합니다.');
        }, 1000);
    }
    
    showError(message) {
        console.error('🚨 에러:', message);
        
        // 간단한 에러 알림 (추후 토스트 알림으로 개선)
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #FF0066, #FF3366);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(255, 0, 102, 0.4);
            z-index: 9999;
            font-weight: 600;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    getCurrentUserDiscordId() {
        // 실제로는 세션에서 가져와야 함
        return window.currentUserDiscordId || 'current_user';
    }
    
    handleRemoteChampionSelection(data) {
        // 다른 플레이어의 선택 처리
        console.log('🎯 원격 선택 처리:', data);
        
        if (data.action === 'ban') {
            this.gameState.bans[data.team].push(data.champion_korean);
        } else {
            this.gameState.picks[data.team].push(data.champion_korean);
            // 팀 구성 업데이트 로직 추가
        }
        
        this.renderChampionGrid();
        this.renderTeamSlots();
    }
    
    updateFromGameState(gameState) {
        // 서버에서 받은 게임 상태로 업데이트
        this.gameState = { ...this.gameState, ...gameState };
        this.renderChampionGrid();
        this.renderTeamSlots();
    }
}

// 전역 변수로 시스템 인스턴스 저장
window.cyberDraftSystem = null;

// 페이지 로드 완료 시 시스템 초기화
document.addEventListener('DOMContentLoaded', function() {
    const sessionId = document.body.dataset.sessionId;
    
    if (sessionId) {
        console.log('🚀 CyberDraftSystem 시작:', sessionId);
        window.cyberDraftSystem = new CyberDraftSystem(sessionId);
    } else {
        console.error('❌ 세션 ID를 찾을 수 없습니다.');
        
        // 개발용: 더미 세션 ID로 테스트
        const dummySessionId = 'cyber_test_' + Date.now();
        console.warn('🧪 더미 세션으로 테스트:', dummySessionId);
        window.cyberDraftSystem = new CyberDraftSystem(dummySessionId);
    }
});

// 브라우저 새로고침/종료 시 정리
window.addEventListener('beforeunload', function() {
    if (window.cyberDraftSystem && window.cyberDraftSystem.socket) {
        window.cyberDraftSystem.socket.disconnect();
    }
});
