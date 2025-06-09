// 중복 로드 방지
if (window.banPickSystemLoaded) {
    console.log('⚠️ banpick.js 이미 로드됨');
} else {
    console.log('✅ banpick.js 로드 시작');
    window.banPickSystemLoaded = true;

    class BanPickSystem {
        constructor(sessionId) {
            this.sessionId = sessionId;
            this.currentUser = null;
            this.socket = io();
            this.gameState = {
                phase: 'position_select',
                teams: {
                    blue: { TOP: null, JUG: null, MID: null, ADC: null, SUP: null },
                    red: { TOP: null, JUG: null, MID: null, ADC: null, SUP: null }
                },
                draft: {
                    bans: { blue: [], red: [] },
                    picks: { blue: [], red: [] },
                    currentTurn: 'blue_ban_1',
                    timer: 30
                }
            };
            this.champions = [];
            
            this.loadCurrentUser();
            this.initializeSocket();
            this.loadChampions();
        }

        async loadCurrentUser() {
            try {
                const response = await fetch('/api/user');
                if (response.ok) {
                    this.currentUser = await response.json();
                    this.displayCurrentUser();
                    console.log(`👤 자동 로그인 완료: ${this.currentUser.final_name || this.currentUser.display_name}`);
                } else {
                    console.log('로그인되지 않음');
                }
            } catch (error) {
                console.error('사용자 정보 로드 실패:', error);
            }
        }

        displayCurrentUser() {
            if (this.currentUser) {
                const existingUserInfo = document.querySelector('.user-info');
                if (existingUserInfo) existingUserInfo.remove();

                const userDisplay = document.createElement('div');
                userDisplay.className = 'user-info';
                userDisplay.innerHTML = `
                    <img src="${this.currentUser.avatar_url}" alt="아바타" class="user-avatar">
                    <span class="user-name">👤 ${this.currentUser.final_name || this.currentUser.display_name}</span>
                    <a href="/auth/logout" class="logout-btn">로그아웃</a>
                `;
                document.querySelector('.header').appendChild(userDisplay);
            }
        }

        initializeSocket() {
            this.socket.on('connect', () => {
                console.log('🔌 WebSocket 연결됨');
                this.socket.emit('join_session', { 
                    session_id: this.sessionId,
                    user_info: this.currentUser 
                });
            });

            this.socket.on('game_state_update', (data) => {
                this.gameState = { ...this.gameState, ...data.game_state };
                this.updateUI();
            });

            this.socket.on('position_selected', (data) => {
                this.handlePositionUpdate(data);
            });
        }

        async loadChampions() {
            try {
                const response = await fetch(`/api/session/${this.sessionId}`);
                const data = await response.json();
                this.champions = data.champions;
                console.log(`📊 ${this.champions.length}개 챔피언 로드됨`);
            } catch (error) {
                console.error('챔피언 데이터 로드 실패:', error);
            }
        }

        selectPosition(team, position) {
            console.log(`🎯 포지션 선택 시도: ${team} ${position}`);
            
            if (!this.currentUser) {
                console.log('❌ 로그인되지 않음');
                if (typeof positionModal !== 'undefined' && positionModal && positionModal.showLoginRequired) {
                    positionModal.showLoginRequired();
                } else {
                    alert('로그인이 필요합니다!');
                }
                return;
            }

            if (this.gameState.teams[team][position]) {
                console.log('❌ 이미 선택된 포지션');
                if (typeof positionModal !== 'undefined' && positionModal && positionModal.showError) {
                    positionModal.showError('이미 선택된 포지션입니다!', '⚠️');
                } else {
                    alert('이미 선택된 포지션입니다!');
                }
                return;
            }

            const userName = this.currentUser.final_name || this.currentUser.display_name;
            const currentPosition = this.findUserPosition(userName);
            
            if (currentPosition) {
                console.log(`🔄 기존 포지션에서 이동: ${currentPosition.team} ${currentPosition.position} → ${team} ${position}`);
                
                // 간단한 확인 모달만 표시
                if (typeof positionModal !== 'undefined' && positionModal && positionModal.showMoveConfirm) {
                    console.log('✅ 변경 확인 모달 사용');
                    positionModal.showMoveConfirm(
                        currentPosition.team, 
                        currentPosition.position, 
                        team, 
                        position, 
                        () => {
                            console.log('🎯 모달에서 변경 확인됨');
                            this.executePositionSelection(team, position);
                        }
                    );
                } else {
                    console.log('❌ 모달 없음, 기본 confirm 사용');
                    if (confirm(`현재 ${currentPosition.team} ${currentPosition.position}에 있습니다. 이동하시겠습니까?`)) {
                        this.executePositionSelection(team, position);
                    }
                }
                return;
            }

            this.executePositionSelection(team, position);
        }

        executePositionSelection(team, position) {
            const userName = this.currentUser.final_name || this.currentUser.display_name;
            console.log(`✅ 포지션 선택 실행: ${userName} → ${team} ${position}`);
            
            this.socket.emit('select_position', {
                session_id: this.sessionId,
                team: team,
                position: position,
                user_name: userName,
                discord_id: this.currentUser.id,
                avatar_url: this.currentUser.avatar_url
            });
            
            // 성공 알림은 UI 업데이트로 충분
        }

        findUserPosition(userName) {
            for (const team of ['blue', 'red']) {
                for (const position of ['TOP', 'JUG', 'MID', 'ADC', 'SUP']) {
                    if (this.gameState.teams[team][position] === userName) {
                        return { team, position };
                    }
                }
            }
            return null;
        }

        handlePositionUpdate(data) {
            console.log(`📡 포지션 업데이트 받음:`, data);
            this.gameState.teams[data.team][data.position] = data.user_name;
            this.updatePositionSlots();
            this.checkAllPositionsFilled();
        }

        updatePositionSlots() {
            ['blue', 'red'].forEach(team => {
                ['TOP', 'JUG', 'MID', 'ADC', 'SUP'].forEach(position => {
                    const slot = document.querySelector(`[data-team="${team}"][data-position="${position}"]`);
                    if (!slot) return;
                    
                    const player = this.gameState.teams[team][position];
                    const playerInfo = slot.querySelector('.player-info');
                    
                    if (player) {
                        slot.classList.add('occupied');
                        const isCurrentUser = this.currentUser && player === (this.currentUser.final_name || this.currentUser.display_name);
                        if (isCurrentUser) {
                            slot.classList.add('current-user');
                        } else {
                            slot.classList.remove('current-user');
                        }
                        
                        playerInfo.innerHTML = `
                            <span class="player-name">${player}</span>
                            ${isCurrentUser ? 
                                `<button class="btn btn-leave" onclick="banPickSystem.leavePosition('${team}', '${position}')">나가기</button>` :
                                '<span class="occupied-text">선택됨</span>'
                            }
                        `;
                    } else {
                        slot.classList.remove('occupied', 'current-user');
                        playerInfo.innerHTML = `
                            <span class="waiting-text">포지션 선택 대기 중</span>
                            <button class="btn btn-join" onclick="banPickSystem.selectPosition('${team}', '${position}')">참가</button>
                        `;
                    }
                });
            });
        }

        leavePosition(team, position) {
            console.log(`🚪 포지션 나가기: ${team} ${position}`);
            this.socket.emit('leave_position', {
                session_id: this.sessionId,
                team: team,
                position: position
            });
        }

        checkAllPositionsFilled() {
            const totalFilled = Object.values(this.gameState.teams.blue).filter(p => p).length +
                               Object.values(this.gameState.teams.red).filter(p => p).length;
            
            const startButton = document.getElementById('startDraftBtn');
            if (startButton) {
                if (totalFilled === 10) {
                    startButton.disabled = false;
                    startButton.textContent = '🚀 밴픽 시작하기';
                    startButton.onclick = () => this.startDraft();
                } else {
                    startButton.disabled = true;
                    startButton.textContent = `포지션 선택 중... (${totalFilled}/10)`;
                }
            }
        }

        updateUI() {
            if (this.gameState.phase === 'position_select') {
                this.updatePositionSlots();
                this.checkAllPositionsFilled();
            }
        }
    }

    // 전역 변수로 시스템 초기화
    let banPickSystem;

    document.addEventListener('DOMContentLoaded', function() {
        if (!window.banPickSystem) {
            const sessionId = document.querySelector('[data-session-id]').dataset.sessionId;
            window.banPickSystem = new BanPickSystem(sessionId);
            console.log('✅ BanPickSystem 초기화 완료');
        }
    });
}
