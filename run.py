#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement unifié pour tous les modes
"""

import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Lanceur unifié du projet')
    parser.add_argument('action', choices=['scrape', 'web'], 
                       help='Action à effectuer')
    parser.add_argument('--mode', choices=['mongo', 'multi'], 
                       default='mongo', help='Mode de scraping')
    parser.add_argument('--count', type=int, default=30, 
                       help='Nombre d\'articles')
    
    args = parser.parse_args()
    
    if args.action == 'scrape':
        # Lancer le scraper
        cmd = [sys.executable, 'scraper_unified.py', 
               '--mode', args.mode, '--count', str(args.count)]
        subprocess.run(cmd)
    
    elif args.action == 'web':
        # Lancer l'interface web
        subprocess.run([sys.executable, 'web_interface.py'])

if __name__ == "__main__":
    main()