console.log('🎭 position_modal.js 로드 시작');

// 중복 로드 방지
if (window.positionModalLoaded) {
    console.log('⚠️ position_modal.js 이미 로드됨');
} else {
    window.positionModalLoaded = true;

    class PositionModal {
        constructor() {
            this.modal = null;
            this.currentCallback = null;
            console.log('🎭 PositionModal 생성됨');
        }

        showMoveConfirm(currentTeam, currentPosition, newTeam, newPosition, callback) {
            console.log('🎭 showMoveConfirm 호출됨');
            
            this.createModal(`
                <div class="modal-header">
                    <h2>🔄 포지션 변경</h2>
                </div>
                <div class="modal-body">
                    <div class="position-change-info">
                        <div class="current-position">
                            <h4>현재 포지션</h4>
                            <div class="position-badge ${currentTeam}">
                                ${this.getTeamIcon(currentTeam)} ${this.getPositionName(currentPosition)}
                            </div>
                        </div>
                        <div class="arrow">→</div>
                        <div class="new-position">
                            <h4>새 포지션</h4>
                            <div class="position-badge ${newTeam}">
                                ${this.getTeamIcon(newTeam)} ${this.getPositionName(newPosition)}
                            </div>
                        </div>
                    </div>
                    <p class="confirm-text">포지션을 변경하시겠습니까?</p>
                    <div class="modal-actions">
                        <button class="btn-cancel" onclick="positionModal.close()">취소</button>
                        <button class="btn-confirm" onclick="positionModal.confirm()">변경하기</button>
                    </div>
                </div>
            `);
            
            this.currentCallback = callback;
        }

        showPositionSelected(team, position, userName) {
            this.createModal(`
                <div class="modal-header">
                    <h2>✅ 포지션 선택 완료</h2>
                </div>
                <div class="modal-body">
                    <div class="success-info">
                        <div class="success-icon">🎯</div>
                        <h3>${userName}</h3>
                        <div class="position-badge ${team}">
                            ${this.getTeamIcon(team)} ${this.getPositionName(position)}
                        </div>
                        <p>포지션이 선택되었습니다!</p>
                    </div>
                    <div class="modal-actions">
                        <button class="btn-ok" onclick="positionModal.close()">확인</button>
                    </div>
                </div>
            `);

            setTimeout(() => this.close(), 3000);
        }

        showError(message, icon = '❌') {
            this.createModal(`
                <div class="modal-header">
                    <h2>${icon} 알림</h2>
                </div>
                <div class="modal-body">
                    <div class="error-info">
                        <div class="error-icon">${icon}</div>
                        <p>${message}</p>
                    </div>
                    <div class="modal-actions">
                        <button class="btn-ok" onclick="positionModal.close()">확인</button>
                    </div>
                </div>
            `);
        }

        showLoginRequired() {
            this.createModal(`
                <div class="modal-header">
                    <h2>🔐 로그인 필요</h2>
                </div>
                <div class="modal-body">
                    <div class="login-required-info">
                        <div class="login-icon">🎮</div>
                        <h3>Discord 로그인이 필요합니다</h3>
                        <p>포지션을 선택하려면 먼저 로그인해주세요.</p>
                    </div>
                    <div class="modal-actions">
                        <button class="btn-cancel" onclick="positionModal.close()">취소</button>
                        <button class="btn-login" onclick="positionModal.loginAndClose()">로그인하기</button>
                    </div>
                </div>
            `);
        }

        createModal(content) {
            // 기존 모달들을 모두 강제 제거
            this.forceCloseAll();

            this.modal = document.createElement('div');
            this.modal.className = 'position-modal';
            this.modal.innerHTML = `
                <div class="modal-overlay" onclick="positionModal.close()"></div>
                <div class="modal-content">${content}</div>
            `;

            document.body.appendChild(this.modal);
            setTimeout(() => this.modal.classList.add('show'), 10);
        }

        confirm() {
            console.log('🎭 모달 확인 버튼 클릭');
            if (this.currentCallback) {
                this.currentCallback();
                this.currentCallback = null;
            }
            this.close();
        }

        loginAndClose() {
            this.close();
            if (typeof loginWithDiscord === 'function') {
                loginWithDiscord();
            }
        }


        forceCloseAll() {
            // 기존 모달 제거
            if (this.modal) {
                this.modal.remove();
                this.modal = null;
            }
            
            // 혹시 남아있는 다른 모달들도 제거
            const existingModals = document.querySelectorAll('.position-modal');
            existingModals.forEach(modal => modal.remove());
            
            this.currentCallback = null;
        }

        close() {
            if (this.modal) {
                this.modal.classList.remove('show');
                setTimeout(() => {
                    if (this.modal) {
                        this.modal.remove();
                        this.modal = null;
                    }
                }, 300);
            }
            this.currentCallback = null;
        }

        getTeamIcon(team) {
            return team === 'blue' ? '🔵' : '🔴';
        }

        getPositionName(position) {
            const positions = {
                'TOP': '탑', 'JUG': '정글', 'MID': '미드',
                'ADC': '원딜', 'SUP': '서포터'
            };
            return positions[position] || position;
        }
    }

    // 전역 객체 생성
    window.positionModal = new PositionModal();
    console.log('🎭 positionModal 전역 객체 생성됨:', window.positionModal);
}
