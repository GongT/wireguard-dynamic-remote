function Set-FolderPermissions {
	param (
		[Parameter(Mandatory = $true)]
		[string]$FolderPath
	)

	# 检查文件夹是否存在
	if (-Not (Test-Path -Path $FolderPath)) {
		Write-Error "文件夹路径不存在: $FolderPath"
		return
	}

	try {
		# 设置所有者为 Administrators 组
		$administrators = New-Object System.Security.Principal.NTAccount("Administrators")
		$acl = Get-Acl -Path $FolderPath
		$acl.SetOwner($administrators)
		Set-Acl -Path $FolderPath -AclObject $acl

		# 禁用继承并移除现有权限
		$acl = Get-Acl -Path $FolderPath
		$acl.SetAccessRuleProtection($true, $false) # 禁用继承，移除现有权限
		Set-Acl -Path $FolderPath -AclObject $acl

		# 授予 Administrators 完全控制权限
		$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
			"Administrators", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
		)
		$acl.AddAccessRule($rule)
		Set-Acl -Path $FolderPath -AclObject $acl

		Write-Host "权限设置完成: $FolderPath"
	} catch {
		Write-Error "设置权限时出错: $_"
	}
}

Set-FolderPermissions C:\ProgramData\WireGuard
