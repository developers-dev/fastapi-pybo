<script>
    import { push } from 'svelte-spa-router';
    import fastapi from "../lib/api";
    import Error from "../components/Error.svelte";

    let error = { detail: [] };
    let current_password = '';
    let new_password = '';
    let new_email = '';

    function changePassword(event) {
        event.preventDefault();
        let url = "/api/user/change-password";
        let params = {
            old_password: current_password,
            new_password: new_password,
        };
        fastapi('post', url, params,
            () => { alert('비밀번호 변경 성공!'); },
            (json_error) => { error = json_error; }
        );
    }

    function changeEmail(event) {
        event.preventDefault();
        let url = "/api/user/change-email";
        let params = { new_email: new_email };
        fastapi('post', url, params,
            () => { alert('이메일 변경 성공!'); },
            (json_error) => { error = json_error; }
        );
    }
</script>

<div class="container">
    <h5 class="my-3 border-bottom pb-2">정보 변경</h5>
    <Error {error} />
    <form method="post">
        <!-- 비밀번호 변경 -->
        <div class="mb-3">
            <label for="current_password">현재 비밀번호</label>
            <input type="password" class="form-control" bind:value={current_password}>
        </div>
        <div class="mb-3">
            <label for="new_password">새 비밀번호</label>
            <input type="password" class="form-control" bind:value={new_password}>
        </div>
        <button class="btn btn-primary" on:click={changePassword}>비밀번호 변경</button>

        <!-- 이메일 변경 -->
        <div class="mb-3">
            <label for="new_email">새 이메일</label>
            <input type="email" class="form-control" bind:value={new_email}>
        </div>
        <button class="btn btn-primary" on:click={changeEmail}>이메일 변경</button>
    </form>
</div>
