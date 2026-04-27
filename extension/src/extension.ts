import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
	console.log('Congratulations, your extension "perf-pilot" is now active!');

	let disposable = vscode.commands.registerCommand('perfpilot.analyze', () => {
		vscode.window.showInformationMessage('PerfPilot: Analyzing code...');
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}
