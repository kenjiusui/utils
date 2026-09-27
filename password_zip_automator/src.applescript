on run {input, parameters}
	if (count of input) is 0 then
		display dialog "対象が渡されていません" buttons {"OK"}
		return
	end if
	
	set pw to text returned of (display dialog "パスワードを入力してください" default answer "" with hidden answer)
	
	set firstPath to POSIX path of (contents of item 1 of input)
	set parentDir to do shell script "dirname " & quoted form of firstPath
	
	set nameList to ""
	repeat with i in input
		set p to POSIX path of (contents of i)
		set n to do shell script "basename " & quoted form of p
		set nameList to nameList & " " & quoted form of n
	end repeat
	
	if (count of input) is 1 then
		set outName to (do shell script "basename " & quoted form of firstPath) & ".zip"
	else
		set outName to "アーカイブ.zip"
	end if
	
	do shell script "cd " & quoted form of parentDir & " && /usr/bin/zip -r -P " & quoted form of pw & " " & quoted form of outName & nameList
	do shell script "open -R " & quoted form of (parentDir & "/" & outName)
	
	return input
end run
