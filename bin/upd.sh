git pull
cd sites_list
git pull
cd ..
if [ -d "$robert_priv" ]; then
  cd robert_priv
  svn up sites_pw.py
  cd ..
fi
